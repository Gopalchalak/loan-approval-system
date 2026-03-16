from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, LoanApplication, Prediction
from ml.predictor import predict_loan

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    apps = LoanApplication.query.filter_by(user_id=current_user.user_id).order_by(LoanApplication.submitted_at.desc()).all()
    total = len(apps)
    approved = sum(1 for a in apps if a.status == 'Approved')
    rejected = sum(1 for a in apps if a.status == 'Rejected')
    pending = sum(1 for a in apps if a.status == 'Pending')
    return render_template('user/dashboard.html', applications=apps, total=total,
                           approved=approved, rejected=rejected, pending=pending)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html')

@user_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if request.method == 'POST':
        try:
            cibil = int(request.form.get('cibil_score', 700))
            credit_history = 1 if cibil >= 650 else 0
            app_data = {
                'loan_type': request.form['loan_type'],
                'gender': request.form['gender'],
                'married': request.form['married'],
                'dependents': request.form['dependents'],
                'education': request.form['education'],
                'employment_status': request.form['self_employed'],
                'applicant_income': float(request.form['applicant_income']),
                'coapplicant_income': float(request.form.get('coapplicant_income', 0) or 0),
                'loan_amount': float(request.form['loan_amount']),
                'loan_tenure': int(request.form['loan_tenure']),
                'credit_history': credit_history,
                'cibil_score': cibil,
                'property_area': request.form['property_area'],
                'existing_loans': int(request.form.get('existing_loans', 0) or 0),
                'purpose': request.form.get('purpose', ''),
            }
            loan = LoanApplication(
                user_id=current_user.user_id,
                loan_type=app_data['loan_type'],
                applicant_income=app_data['applicant_income'],
                coapplicant_income=app_data['coapplicant_income'],
                loan_amount=app_data['loan_amount'],
                loan_tenure=app_data['loan_tenure'],
                credit_history=app_data['credit_history'],
                cibil_score=app_data['cibil_score'],
                employment_status=app_data['employment_status'],
                property_area=app_data['property_area'],
                education=app_data['education'],
                dependents=app_data['dependents'],
                gender=app_data['gender'],
                married=app_data['married'],
                existing_loans=app_data['existing_loans'],
                purpose=app_data['purpose'],
                status='Pending'
            )
            db.session.add(loan)
            db.session.flush()

            result = predict_loan(app_data)
            pred = Prediction(
                application_id=loan.application_id,
                predicted_result=result['result'],
                probability=result['probability'],
                risk_level=result['risk_level'],
                model_used='Random Forest'
            )
            db.session.add(pred)
            db.session.commit()
            flash('Application submitted! Your AI prediction is ready.', 'success')
            return redirect(url_for('user.result', app_id=loan.application_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('user/apply.html')

@user_bp.route('/result/<int:app_id>')
@login_required
def result(app_id):
    loan = LoanApplication.query.get_or_404(app_id)
    if loan.user_id != current_user.user_id and not current_user.is_admin:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.dashboard'))
    pred = Prediction.query.filter_by(application_id=app_id).first()
    return render_template('user/result.html', loan=loan, prediction=pred)

@user_bp.route('/applications')
@login_required
def applications():
    apps = LoanApplication.query.filter_by(user_id=current_user.user_id).order_by(LoanApplication.submitted_at.desc()).all()
    return render_template('user/applications.html', applications=apps)
