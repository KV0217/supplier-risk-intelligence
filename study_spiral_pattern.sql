-- Study Spiral Pattern Detection
-- Find students who study multiple subjects in a repeating cycle

WITH student_sessions AS (
    -- Get all study sessions ordered by student and date
    SELECT 
        s.student_id,
        st.student_name,
        st.major,
        s.subject,
        s.session_date,
        s.hours_studied,
        ROW_NUMBER() OVER (PARTITION BY s.student_id ORDER BY s.session_date) as session_num,
        -- Calculate days gap from previous session
        DATEDIFF(s.session_date, 
                 LAG(s.session_date) OVER (PARTITION BY s.student_id ORDER BY s.session_date)) as days_gap
    FROM study_sessions s
    JOIN students st ON s.student_id = st.student_id
),
valid_sequences AS (
    -- Filter out sessions with gaps > 2 days (start new sequence)
    SELECT 
        *,
        SUM(CASE WHEN days_gap IS NULL OR days_gap <= 2 THEN 0 ELSE 1 END) 
            OVER (PARTITION BY student_id ORDER BY session_num) as sequence_id
    FROM student_sessions
),
grouped_sequences AS (
    -- Group sessions into sequences (consecutive dates with no gap > 2 days)
    SELECT 
        student_id,
        student_name,
        major,
        sequence_id,
        COUNT(*) as session_count,
        SUM(hours_studied) as total_hours,
        STRING_AGG(subject, ',' ORDER BY session_num) as subject_sequence
    FROM valid_sequences
    GROUP BY student_id, student_name, major, sequence_id
    HAVING COUNT(*) >= 6  -- Minimum 6 sessions for 2 complete cycles
),
pattern_detection AS (
    -- Detect repeating pattern in subject sequence
    SELECT 
        student_id,
        student_name,
        major,
        total_hours,
        session_count,
        -- Count unique subjects in the sequence
        (SELECT COUNT(DISTINCT subject) 
         FROM valid_sequences v2 
         WHERE v2.student_id = grouped_sequences.student_id 
         AND v2.sequence_id = grouped_sequences.sequence_id) as cycle_length
    FROM grouped_sequences
)
SELECT 
    student_id,
    student_name,
    major,
    cycle_length,
    total_hours as total_study_hours
FROM pattern_detection
WHERE cycle_length >= 3  -- Minimum 3 subjects in cycle
ORDER BY cycle_length DESC, total_study_hours DESC;
