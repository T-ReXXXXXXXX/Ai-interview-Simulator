import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "interview_results.db"

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            profile_picture TEXT,
            role TEXT DEFAULT 'employee',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add role column to users table if it doesn't exist (migration for existing databases)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'employee'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Interview results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            interview_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            questions_count INTEGER,
            overall_score REAL,
            feedback TEXT,
            resume_data TEXT,
            answers TEXT,
            emotion_data TEXT,
            scheduled_by TEXT,
            FOREIGN KEY (email) REFERENCES users(email)
        )
    """)
    
    # Add scheduled_by column to interview_results table if it doesn't exist (migration)
    try:
        cursor.execute("ALTER TABLE interview_results ADD COLUMN scheduled_by TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Scheduled interviews table (for admin to schedule interviews for users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheduled_by TEXT NOT NULL,
            user_email TEXT NOT NULL,
            user_name TEXT,
            scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            FOREIGN KEY (scheduled_by) REFERENCES users(email),
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)
    
    conn.commit()
    conn.close()

def get_or_create_user(email, name=None, profile_picture=None, role='employee'):
    """Get existing user or create new one"""
    email = email.lower().strip()  # Normalize email to lowercase
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    
    if result:
        user_id = result[0]
        # Update profile picture if provided
        if profile_picture:
            cursor.execute(
                "UPDATE users SET profile_picture = ? WHERE email = ?",
                (profile_picture, email)
            )
            conn.commit()
    else:
        cursor.execute(
            "INSERT INTO users (email, name, profile_picture, role) VALUES (?, ?, ?, ?)",
            (email, name, profile_picture, role)
        )
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cursor.fetchone()[0]
    
    conn.close()
    return user_id

def save_interview_result(email, questions_count, overall_score, feedback, resume_data=None, answers=None, emotion_data=None, scheduled_by=None):
    """Save interview result for a user"""
    email = email.lower().strip()  # Normalize email to lowercase
    if scheduled_by:
        scheduled_by = scheduled_by.lower().strip()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if not cursor.fetchone():
        get_or_create_user(email)
    
    cursor.execute("""
        INSERT INTO interview_results 
        (email, questions_count, overall_score, feedback, resume_data, answers, emotion_data, scheduled_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email,
        questions_count,
        overall_score,
        feedback,
        json.dumps(resume_data) if resume_data else None,
        json.dumps(answers) if answers else None,
        json.dumps(emotion_data) if emotion_data else None,
        scheduled_by
    ))
    
    conn.commit()
    conn.close()

def get_admin_for_scheduled_interview(user_email):
    """Get admin details (email and name) who scheduled interview for this user"""
    user_email = user_email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the most recent scheduled interview for this user
    cursor.execute("""
        SELECT scheduled_by
        FROM scheduled_interviews
        WHERE user_email = ?
        ORDER BY scheduled_at DESC
        LIMIT 1
    """, (user_email,))
    
    result = cursor.fetchone()
    if result:
        admin_email = result[0]
        # Get admin details
        cursor.execute(
            "SELECT name, email FROM users WHERE email = ?",
            (admin_email,)
        )
        admin_result = cursor.fetchone()
        conn.close()
        if admin_result:
            return {
                'email': admin_email,
                'name': admin_result[0]
            }
    
    conn.close()
    return None

def get_user_results(email):
    """Get all interview results for a user"""
    email = email.lower().strip()  # Normalize email to lowercase
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, interview_date, questions_count, overall_score, feedback, 
            resume_data, answers, emotion_data
        FROM interview_results
        WHERE email = ?
        ORDER BY interview_date DESC
    """, (email,))
    
    results = cursor.fetchall()
    conn.close()
    
    formatted_results = []
    for result in results:
        formatted_results.append({
            'id': result[0],
            'date': result[1],
            'questions_count': result[2],
            'overall_score': result[3],
            'feedback': result[4],
            'resume_data': json.loads(result[5]) if result[5] else None,
            'answers': json.loads(result[6]) if result[6] else None,
            'emotion_data': json.loads(result[7]) if result[7] else None
        })
    
    return formatted_results

def get_user_info(email):
    """Get user information"""
    email = email.lower().strip()  # Normalize email to lowercase
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, profile_picture, role, created_at FROM users WHERE email = ?",
        (email,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'email': email,
            'name': result[1],
            'profile_picture': result[2],
            'role': result[3],
            'created_at': result[4]
        }
    return None

def get_all_user_stats(email):
    """Get aggregated stats for a user"""
    email = email.lower().strip()  # Normalize email to lowercase
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_attempts,
            AVG(overall_score) as avg_score,
            MAX(overall_score) as best_score,
            MIN(overall_score) as worst_score
        FROM interview_results
        WHERE email = ?
    """, (email,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] > 0:
        return {
            'total_attempts': result[0],
            'avg_score': round(result[1], 2),
            'best_score': result[2],
            'worst_score': result[3]
        }
    return {
        'total_attempts': 0,
        'avg_score': 0,
        'best_score': 0,
        'worst_score': 0
    }

def get_user_role(email):
    """Get user role"""
    email = email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT role FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 'user'

def schedule_interview(admin_email, user_email, user_name, notes=""):
    """Schedule interview for a user (admin function)"""
    admin_email = admin_email.lower().strip()
    user_email = user_email.lower().strip()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO scheduled_interviews (scheduled_by, user_email, user_name, notes)
        VALUES (?, ?, ?, ?)
    """, (admin_email, user_email, user_name, notes))
    
    conn.commit()
    conn.close()

def get_scheduled_interviews_by_admin(admin_email):
    """Get all interviews scheduled by this admin"""
    admin_email = admin_email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_email, user_name, scheduled_at, status, notes
        FROM scheduled_interviews
        WHERE scheduled_by = ?
        ORDER BY scheduled_at DESC
    """, (admin_email,))
    
    results = cursor.fetchall()
    conn.close()
    
    formatted_results = []
    for result in results:
        formatted_results.append({
            'id': result[0],
            'user_email': result[1],
            'user_name': result[2],
            'scheduled_at': result[3],
            'status': result[4],
            'notes': result[5]
        })
    
    return formatted_results

def get_scheduled_interviews_for_user(user_email):
    """Get all interviews scheduled for this user by admins"""
    user_email = user_email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, scheduled_by, user_name, scheduled_at, status, notes
        FROM scheduled_interviews
        WHERE user_email = ?
        ORDER BY scheduled_at DESC
    """, (user_email,))
    
    results = cursor.fetchall()
    conn.close()
    
    formatted_results = []
    for result in results:
        formatted_results.append({
            'id': result[0],
            'scheduled_by': result[1],
            'user_name': result[2],
            'scheduled_at': result[3],
            'status': result[4],
            'notes': result[5]
        })
    
    return formatted_results

def update_scheduled_interview_status_by_user(user_email, status):
    """Update scheduled interview status by user email"""
    user_email = user_email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE scheduled_interviews SET status = ? WHERE user_email = ?
    """, (status, user_email))
    
    conn.commit()
    conn.close()

def update_scheduled_interview_status(interview_id, status):
    """Update scheduled interview status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE scheduled_interviews SET status = ? WHERE id = ?
    """, (status, interview_id))
    
    conn.commit()
    conn.close()

def get_all_users():
    """Get list of all users in the system"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email, name, role, created_at FROM users 
        ORDER BY created_at DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    formatted_results = []
    for result in results:
        formatted_results.append({
            'id': result[0],
            'email': result[1],
            'name': result[2],
            'role': result[3],
            'created_at': result[4]
        })
    
    return formatted_results

def update_user_role(email, role):
    """Update user role (interviewer or employee)"""
    email = email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET role = ? WHERE email = ?
    """, (role, email))
    
    conn.commit()
    conn.close()

def get_user_interview_count(email):
    """Get total interview attempts for a user"""
    email = email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM interview_results WHERE email = ?
    """, (email,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0

# Initialize database on import
init_database()
