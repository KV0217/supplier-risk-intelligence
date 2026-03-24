#!/usr/bin/env python3
"""
Quick Start Script for Supplier Risk Intelligence System
Run this to test the entire pipeline end-to-end
"""

import sys
import subprocess
import os
from pathlib import Path

def print_banner():
    print("\n" + "="*70)
    print(" 📊 SUPPLIER RISK INTELLIGENCE SYSTEM - QUICK START")
    print("="*70 + "\n")

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['pandas', 'streamlit', 'plotly', 'feedparser']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstalling missing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully\n")
    else:
        print("\n✅ All dependencies installed\n")

def run_analysis():
    """Run the analysis notebook"""
    print("\n" + "="*70)
    print(" 📈 RUNNING ANALYSIS & RISK SCORING")
    print("="*70 + "\n")
    
    try:
        import pandas as pd
        from data_collector import DataCollector
        from risk_scoring import RiskScoringEngine
        
        # Collect data
        print("🔄 Collecting supplier data...")
        collector = DataCollector()
        news_df, financial_df = collector.collect_all_data()
        
        print(f"✅ Collected {len(news_df)} news articles")
        print(f"✅ Collected financial data for {len(financial_df)} companies\n")
        
        # Score suppliers
        print("🔄 Calculating risk scores...")
        engine = RiskScoringEngine()
        risk_scores = engine.score_suppliers(news_df, financial_df)
        
        print("✅ Risk assessment complete\n")
        
        # Display results
        print("="*70)
        print(" 📊 RISK ASSESSMENT RESULTS")
        print("="*70 + "\n")
        
        print(f"Total Suppliers: {len(risk_scores)}")
        print(f"Average Risk Score: {risk_scores['risk_score'].mean():.1f}/100")
        print(f"Critical Risks: {len(risk_scores[risk_scores['risk_score'] >= 75])}")
        print(f"High Risks: {len(risk_scores[(risk_scores['risk_score'] >= 60) & (risk_scores['risk_score'] < 75)])}")
        print(f"Stable Suppliers: {len(risk_scores[risk_scores['risk_score'] < 40])}\n")
        
        print("Top 5 Riskiest Suppliers:")
        for idx, row in risk_scores.head(5).iterrows():
            print(f"  {idx+1}. {row['company']}: {row['risk_score']:.1f} {row['risk_level']}")
        
        # Save results
        risk_scores.to_csv('supplier_risk_assessment.csv', index=False)
        print("\n✅ Results saved to 'supplier_risk_assessment.csv'\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("\n" + "="*70)
    print(" 🎯 LAUNCHING STREAMLIT DASHBOARD")
    print("="*70 + "\n")
    
    print("Dashboard will open in your browser at: http://localhost:8501\n")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=False)
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")

def show_menu():
    """Show interactive menu"""
    while True:
        print("\n" + "="*70)
        print(" 🎯 SUPPLIER RISK INTELLIGENCE - MAIN MENU")
        print("="*70)
        print("\n  1. Check Dependencies")
        print("  2. Run Analysis & Risk Scoring")
        print("  3. Launch Streamlit Dashboard")
        print("  4. Run Full Pipeline (2 + 3)")
        print("  5. View Results (CSV)")
        print("  6. View Configuration")
        print("  7. Exit")
        print("\n" + "-"*70)
        
        choice = input("Select option (1-7): ").strip()
        
        if choice == '1':
            check_dependencies()
        elif choice == '2':
            run_analysis()
        elif choice == '3':
            launch_dashboard()
        elif choice == '4':
            if run_analysis():
                response = input("\n🎯 Dashboard ready. Launch it now? (y/n): ").strip().lower()
                if response == 'y':
                    launch_dashboard()
        elif choice == '5':
            if Path('supplier_risk_assessment.csv').exists():
                print("\n📊 Recent Results:")
                import pandas as pd
                df = pd.read_csv('supplier_risk_assessment.csv')
                print(df.to_string(index=False))
            else:
                print("\n⚠️  No results found. Run analysis first.")
        elif choice == '6':
            print("\n📋 Configuration Summary:")
            try:
                from config import RISK_THRESHOLDS, SUPPLIERS
                print(f"  Risk Thresholds: {RISK_THRESHOLDS}")
                print(f"  Monitored Suppliers: {len(SUPPLIERS)}")
            except:
                print("  (Config module not available)")
        elif choice == '7':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid option. Please select 1-7.")

def main():
    """Main entry point"""
    print_banner()
    
    # Check if running in headless mode
    if len(sys.argv) > 1:
        if sys.argv[1] == '--full':
            print("🚀 Running full pipeline...\n")
            check_dependencies()
            if run_analysis():
                print("\n✅ Analysis complete!")
                print("\n📊 To view dashboard, run: streamlit run app.py")
        elif sys.argv[1] == '--analysis':
            check_dependencies()
            run_analysis()
        elif sys.argv[1] == '--dashboard':
            check_dependencies()
            launch_dashboard()
        elif sys.argv[1] == '--help':
            print("Usage: python quickstart.py [OPTION]\n")
            print("Options:")
            print("  --full      Run complete pipeline (analysis + dashboard)")
            print("  --analysis  Run analysis only")
            print("  --dashboard Launch dashboard only")
            print("  (no args)   Interactive menu\n")
    else:
        # Interactive menu
        try:
            show_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
