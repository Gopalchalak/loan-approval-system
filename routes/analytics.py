from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import LoanApplication, Prediction
from collections import Counter

analytics_bp = Blueprint('analytics', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            from flask import flash, redirect, url_for
            flash('Admin access required for Analytics.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@analytics_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    return render_template('analytics/dashboard.html')

@analytics_bp.route('/api/analytics/overview')
@login_required
@admin_required
def overview_data():
    apps = LoanApplication.query.all()
    status_counts = Counter(a.status for a in apps)
    credit_approval = {
        'Good Credit (650+)': {'Approved': 0, 'Rejected': 0, 'Pending': 0},
        'Poor Credit (<650)': {'Approved': 0, 'Rejected': 0, 'Pending': 0}
    }
    for a in apps:
        key = 'Good Credit (650+)' if a.credit_history == 1 else 'Poor Credit (<650)'
        credit_approval[key][a.status] = credit_approval[key].get(a.status, 0) + 1

    property_counts = Counter(a.property_area for a in apps)
    loan_type_counts = Counter(a.loan_type for a in apps if hasattr(a, 'loan_type') and a.loan_type)
    education_approval = {}
    for a in apps:
        if a.education not in education_approval:
            education_approval[a.education] = {'Approved': 0, 'Rejected': 0, 'Pending': 0}
        education_approval[a.education][a.status] += 1

    preds = Prediction.query.all()
    risk_counts = Counter(p.risk_level for p in preds)
    loan_amounts = [a.loan_amount for a in apps]

    return jsonify({
        'status_counts': dict(status_counts),
        'credit_approval': credit_approval,
        'loan_amounts': loan_amounts,
        'property_counts': dict(property_counts),
        'education_approval': education_approval,
        'risk_counts': dict(risk_counts),
        'loan_type_counts': dict(loan_type_counts),
        'total_apps': len(apps)
    })
