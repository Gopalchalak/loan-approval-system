import sqlite3
import bcrypt
from config import Config
from datetime import datetime

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Loan Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            applicant_income REAL NOT NULL,
            coapplicant_income REAL DEFAULT 0,
            loan_amount REAL NOT NULL,
            loan_amount_term INTEGER NOT NULL,
            credit_history INTEGER NOT NULL,
            employment_status TEXT NOT NULL,
            property_area TEXT NOT NULL,
            education TEXT NOT NULL,
            dependents TEXT NOT NULL,
            gender TEXT,
            married TEXT,
            self_employed TEXT,
            status TEXT DEFAULT 'Pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            predicted_result TEXT NOT NULL,
            probability REAL NOT NULL,
            risk_level TEXT NOT NULL,
            model_used TEXT NOT NULL,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        )
    ''')
    
    # Admin Decisions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            admin_id INTEGER NOT NULL,
            admin_decision TEXT NOT NULL,
            remarks TEXT,
            decision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES loan_applications(application_id),
            FOREIGN KEY (admin_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    
    # Create default admin if not exists
    cursor.execute('SELECT * FROM users WHERE email = ?', (Config.ADMIN_EMAIL,))
    if not cursor.fetchone():
        hashed = bcrypt.hashpw(Config.ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('''
            INSERT INTO users (name, email, password, phone, address, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Administrator', Config.ADMIN_EMAIL, hashed.decode('utf-8'),
              '9999999999', 'Admin HQ, Financial District', 1))
        conn.commit()
    
    conn.close()

# ─── USER FUNCTIONS ───────────────────────────────────────────────────────────

def create_user(name, email, password, phone='', address=''):
    conn = get_db()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password, phone, address)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, hashed.decode('utf-8'), phone, address))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def verify_password(email, password):
    user = get_user_by_email(email)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

def update_user_profile(user_id, name, phone, address):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET name=?, phone=?, address=? WHERE user_id=?
    ''', (name, phone, address, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE is_admin = 0 ORDER BY created_at DESC')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

# ─── LOAN APPLICATION FUNCTIONS ───────────────────────────────────────────────

def create_loan_application(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO loan_applications 
        (user_id, applicant_income, coapplicant_income, loan_amount, loan_amount_term,
         credit_history, employment_status, property_area, education, dependents,
         gender, married, self_employed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['user_id'], data['applicant_income'], data.get('coapplicant_income', 0),
        data['loan_amount'], data['loan_amount_term'], data['credit_history'],
        data['employment_status'], data['property_area'], data['education'],
        data['dependents'], data.get('gender', 'Male'), data.get('married', 'No'),
        data.get('self_employed', 'No')
    ))
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    return app_id

def get_application_by_id(app_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT la.*, u.name as applicant_name, u.email as applicant_email,
               p.predicted_result, p.probability, p.risk_level, p.model_used,
               ad.admin_decision, ad.remarks, ad.decision_date
        FROM loan_applications la
        JOIN users u ON la.user_id = u.user_id
        LEFT JOIN predictions p ON la.application_id = p.application_id
        LEFT JOIN admin_decisions ad ON la.application_id = ad.application_id
        WHERE la.application_id = ?
    ''', (app_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_applications(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT la.*, p.predicted_result, p.probability, p.risk_level,
               ad.admin_decision
        FROM loan_applications la
        LEFT JOIN predictions p ON la.application_id = p.application_id
        LEFT JOIN admin_decisions ad ON la.application_id = ad.application_id
        WHERE la.user_id = ?
        ORDER BY la.applied_at DESC
    ''', (user_id,))
    apps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return apps

def get_all_applications():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT la.*, u.name as applicant_name, u.email as applicant_email,
               p.predicted_result, p.probability, p.risk_level,
               ad.admin_decision, ad.decision_date
        FROM loan_applications la
        JOIN users u ON la.user_id = u.user_id
        LEFT JOIN predictions p ON la.application_id = p.application_id
        LEFT JOIN admin_decisions ad ON la.application_id = ad.application_id
        ORDER BY la.applied_at DESC
    ''')
    apps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return apps

def update_application_status(app_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE loan_applications SET status=? WHERE application_id=?', (status, app_id))
    conn.commit()
    conn.close()

# ─── PREDICTION FUNCTIONS ─────────────────────────────────────────────────────

def save_prediction(app_id, result, probability, risk_level, model_used):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions WHERE application_id = ?', (app_id,))
    cursor.execute('''
        INSERT INTO predictions (application_id, predicted_result, probability, risk_level, model_used)
        VALUES (?, ?, ?, ?, ?)
    ''', (app_id, result, probability, risk_level, model_used))
    conn.commit()
    conn.close()

def get_prediction_by_app(app_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions WHERE application_id = ?', (app_id,))
    pred = cursor.fetchone()
    conn.close()
    return dict(pred) if pred else None

# ─── ADMIN DECISION FUNCTIONS ─────────────────────────────────────────────────

def save_admin_decision(app_id, admin_id, decision, remarks=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admin_decisions WHERE application_id = ?', (app_id,))
    cursor.execute('''
        INSERT INTO admin_decisions (application_id, admin_id, admin_decision, remarks)
        VALUES (?, ?, ?, ?)
    ''', (app_id, admin_id, decision, remarks))
    conn.commit()
    # Update application status
    cursor.execute('UPDATE loan_applications SET status=? WHERE application_id=?',
                   (decision, app_id))
    conn.commit()
    conn.close()

# ─── ANALYTICS FUNCTIONS ──────────────────────────────────────────────────────

def get_analytics_data():
    conn = get_db()
    cursor = conn.cursor()
    
    data = {}
    
    # Total counts
    cursor.execute('SELECT COUNT(*) as total FROM loan_applications')
    data['total_applications'] = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM users WHERE is_admin = 0')
    data['total_users'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM predictions WHERE predicted_result = 'Approved'")
    data['ml_approved'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM predictions WHERE predicted_result = 'Rejected'")
    data['ml_rejected'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM admin_decisions WHERE admin_decision = 'Approved'")
    data['admin_approved'] = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM admin_decisions WHERE admin_decision = 'Rejected'")
    data['admin_rejected'] = cursor.fetchone()['total']
    
    # Risk level distribution
    cursor.execute('SELECT risk_level, COUNT(*) as count FROM predictions GROUP BY risk_level')
    data['risk_distribution'] = {row['risk_level']: row['count'] for row in cursor.fetchall()}
    
    # Credit history vs approval
    cursor.execute('''
        SELECT la.credit_history, p.predicted_result, COUNT(*) as count
        FROM loan_applications la
        JOIN predictions p ON la.application_id = p.application_id
        GROUP BY la.credit_history, p.predicted_result
    ''')
    data['credit_history_data'] = [dict(row) for row in cursor.fetchall()]
    
    # Loan amount distribution
    cursor.execute('SELECT loan_amount FROM loan_applications')
    data['loan_amounts'] = [row['loan_amount'] for row in cursor.fetchall()]
    
    # Education vs approval
    cursor.execute('''
        SELECT la.education, p.predicted_result, COUNT(*) as count
        FROM loan_applications la
        JOIN predictions p ON la.application_id = p.application_id
        GROUP BY la.education, p.predicted_result
    ''')
    data['education_data'] = [dict(row) for row in cursor.fetchall()]
    
    # Property area vs approval
    cursor.execute('''
        SELECT la.property_area, p.predicted_result, COUNT(*) as count
        FROM loan_applications la
        JOIN predictions p ON la.application_id = p.application_id
        GROUP BY la.property_area, p.predicted_result
    ''')
    data['property_data'] = [dict(row) for row in cursor.fetchall()]
    
    # Monthly applications
    cursor.execute('''
        SELECT strftime('%Y-%m', applied_at) as month, COUNT(*) as count
        FROM loan_applications
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    ''')
    data['monthly_apps'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return data
