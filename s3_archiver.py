"""
AWS S3 Archiver — Supplier Risk Intelligence System
====================================================
Archives real-time supplier risk assessment reports to AWS S3 for
audit trails, historical trend analysis, and compliance reporting.
Integrates directly with the existing Airflow DAG and Streamlit dashboard.

Setup:
    pip install boto3 python-dotenv

    Create a .env file with:
        AWS_ACCESS_KEY_ID=<your-key>
        AWS_SECRET_ACCESS_KEY=<your-secret>
        AWS_REGION=ap-south-1
        S3_BUCKET_NAME=supplier-risk-intelligence-kv

Usage:
    python s3_archiver.py                  # demo run
    from s3_archiver import archive_report # import into Airflow DAG
"""

import os
import io
import gzip
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION     = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET      = os.getenv("S3_BUCKET_NAME", "supplier-risk-intelligence-kv")

# S3 key structure:  reports/YYYY/MM/DD/<company>_HH-MM-SS.json.gz
KEY_PREFIX = "reports"


class S3Archiver:
    """
    Handles compressed archiving and retrieval of supplier risk reports
    to/from AWS S3 — supports audit trails, versioning, and trend analysis.
    """

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION,
        )
        self.bucket = S3_BUCKET
        self._ensure_bucket()

    # ── Bucket Management ─────────────────────────────────────────────────────

    def _ensure_bucket(self) -> None:
        """Create the S3 bucket (with versioning) if it does not exist."""
        try:
            self.s3.head_bucket(Bucket=self.bucket)
            logger.info(f"S3 bucket '{self.bucket}' found.")
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            if code in ("404", "NoSuchBucket"):
                logger.info(f"Creating S3 bucket '{self.bucket}' in {AWS_REGION} …")
                if AWS_REGION == "us-east-1":
                    self.s3.create_bucket(Bucket=self.bucket)
                else:
                    self.s3.create_bucket(
                        Bucket=self.bucket,
                        CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
                    )
                # Enable versioning for immutable audit trail
                self.s3.put_bucket_versioning(
                    Bucket=self.bucket,
                    VersioningConfiguration={"Status": "Enabled"},
                )
                # Block all public access
                self.s3.put_public_access_block(
                    Bucket=self.bucket,
                    PublicAccessBlockConfiguration={
                        "BlockPublicAcls": True,
                        "IgnorePublicAcls": True,
                        "BlockPublicPolicy": True,
                        "RestrictPublicBuckets": True,
                    },
                )
                logger.info("Bucket created with versioning + public-access block enabled.")
            else:
                raise

    # ── Key Builder ───────────────────────────────────────────────────────────

    @staticmethod
    def _build_key(company: str, ts: datetime) -> str:
        date_str = ts.strftime("%Y/%m/%d")
        time_str = ts.strftime("%H-%M-%S")
        safe     = company.lower().replace(" ", "_").replace("/", "-")
        return f"{KEY_PREFIX}/{date_str}/{safe}_{time_str}.json.gz"

    # ── Upload ────────────────────────────────────────────────────────────────

    def archive_report(self, report: dict, company: str) -> str:
        """
        Compress and upload a risk assessment report dict to S3.
        Called by the Airflow DAG after each assessment cycle.
        Returns the S3 URI of the stored object.
        """
        ts = datetime.now(timezone.utc)
        key = self._build_key(company, ts)

        report["_metadata"] = {
            "company":        company,
            "archived_at":    ts.isoformat(),
            "bucket":         self.bucket,
            "key":            key,
            "schema_version": "1.0",
        }

        compressed = gzip.compress(
            json.dumps(report, default=str).encode("utf-8"), compresslevel=9
        )

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=compressed,
            ContentType="application/json",
            ContentEncoding="gzip",
            Metadata={
                "company":    company,
                "risk_level": str(report.get("risk_level", "UNKNOWN")),
                "risk_score": str(round(float(report.get("risk_score", 0)), 2)),
            },
        )

        uri = f"s3://{self.bucket}/{key}"
        logger.info(f"Archived '{company}' report  →  {uri}  ({len(compressed)} bytes compressed)")
        return uri

    # ── List & Download ───────────────────────────────────────────────────────

    def list_reports(
        self,
        company: Optional[str] = None,
        date_prefix: Optional[str] = None,   # e.g. "2025/07"
    ) -> list[dict]:
        """List archived reports, optionally filtered by company name or date."""
        prefix = f"{KEY_PREFIX}/{date_prefix}" if date_prefix else KEY_PREFIX
        paginator = self.s3.get_paginator("list_objects_v2")
        results = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                if company is None or company.lower() in obj["Key"].lower():
                    results.append({
                        "key":           obj["Key"],
                        "size_bytes":    obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                        "s3_uri":        f"s3://{self.bucket}/{obj['Key']}",
                    })
        logger.info(f"Found {len(results)} report(s).")
        return results

    def download_report(self, s3_key: str) -> dict:
        """Download and decompress a single report from S3."""
        response = self.s3.get_object(Bucket=self.bucket, Key=s3_key)
        raw      = response["Body"].read()
        data     = gzip.decompress(raw)
        return json.loads(data.decode("utf-8"))

    # ── Historical Trend ──────────────────────────────────────────────────────

    def get_risk_trend(self, company: str) -> list[dict]:
        """
        Return chronological risk score history for one company.
        Used by the Streamlit dashboard for trend charts.
        """
        reports = self.list_reports(company=company)
        trend   = []
        for r in reports:
            try:
                data = self.download_report(r["key"])
                trend.append({
                    "archived_at": data.get("_metadata", {}).get("archived_at"),
                    "risk_score":  data.get("risk_score"),
                    "risk_level":  data.get("risk_level"),
                    "company":     company,
                })
            except Exception as exc:
                logger.warning(f"Skipping {r['key']}: {exc}")
        return sorted(trend, key=lambda x: x.get("archived_at") or "")

    # ── Presigned URL (share reports without credentials) ─────────────────────

    def get_presigned_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate a time-limited presigned URL for sharing a specific report."""
        url = self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": s3_key},
            ExpiresIn=expires_in,
        )
        logger.info(f"Presigned URL (expires in {expires_in}s): {url}")
        return url


# ── Module-level helpers (imported by Airflow DAG / api.py) ──────────────────

_archiver: Optional[S3Archiver] = None


def _get_archiver() -> S3Archiver:
    global _archiver
    if _archiver is None:
        _archiver = S3Archiver()
    return _archiver


def archive_report(report: dict, company: str) -> str:
    """Top-level helper — call this from the Airflow DAG after each assessment."""
    return _get_archiver().archive_report(report, company)


def get_risk_history(company: str) -> list[dict]:
    """Return historical trend data — call from Streamlit dashboard."""
    return _get_archiver().get_risk_trend(company)


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_report = {
        "company":          "Intel",
        "risk_score":       68.5,
        "risk_level":       "HIGH",
        "news_risk":        55.0,
        "financial_risk":   82.0,
        "recent_articles":  14,
        "assessment_date":  datetime.now(timezone.utc).isoformat(),
    }

    print("── Archiving report …")
    uri = archive_report(sample_report, "Intel")
    print(f"   Stored at: {uri}")

    print("\n── All reports in S3:")
    archiver = _get_archiver()
    for r in archiver.list_reports():
        print(f"   {r['s3_uri']}  ({r['size_bytes']} bytes)")

    print("\n── Risk trend for Intel:")
    for t in get_risk_history("Intel"):
        print(f"   {t}")
