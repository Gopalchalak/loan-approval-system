from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import User, LoanApplication, Prediction, AdminDecision

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    total_apps = LoanApplication.query.count()
    approved = LoanApplication.query.filter_by(status='Approved').count()
    rejected = LoanApplication.query.filter_by(status='Rejected').count()
    pending = LoanApplication.query.filter_by(status='Pending').count()
    recent_apps = LoanApplication.query.order_by(LoanApplication.submitted_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', total_users=total_users, total_apps=total_apps,
                           approved=approved, rejected=rejected, pending=pending, recent_apps=recent_apps)

@admin_bp.route('/applications')
@login_required
@admin_required
def applications():
    status_filter = request.args.get('status', 'all')
    query = LoanApplication.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    apps = query.order_by(LoanApplication.submitted_at.desc()).all()
    return render_template('admin/applications.html', applications=apps, status_filter=status_filter)

@admin_bp.route('/application/<int:app_id>')
@login_required
@admin_required
def view_application(app_id):
    loan = LoanApplication.query.get_or_404(app_id)
    pred = Prediction.query.filter_by(application_id=app_id).first()
    decisions = AdminDecision.query.filter_by(application_id=app_id).all()
    return render_template('admin/view_application.html', loan=loan, prediction=pred, decisions=decisions)

@admin_bp.route('/decide/<int:app_id>', methods=['POST'])
@login_required
@admin_required
def decide(app_id):
    loan = LoanApplication.query.get_or_404(app_id)
    decision = request.form.get('decision')
    remarks = request.form.get('remarks', '')
    if decision not in ['Approved', 'Rejected']:
        flash('Invalid decision.', 'danger')
        return redirect(url_for('admin.view_application', app_id=app_id))
    loan.status = decision
    admin_dec = AdminDecision(application_id=app_id, admin_id=current_user.user_id,
                               admin_decision=decision, remarks=remarks)
    db.session.add(admin_dec)
    db.session.commit()
    flash(f'Application {decision} successfully.', 'success')
    return redirect(url_for('admin.applications'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.address = request.form.get('address', '').strip()
        new_pw = request.form.get('new_password', '')
        if new_pw:
            current_user.set_password(new_pw)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin.profile'))
    return render_template('admin/profile.html')
