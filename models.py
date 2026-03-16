from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('LoanApplication', backref='applicant', lazy=True)

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class LoanApplication(db.Model):
    __tablename__ = 'loan_applications'
    application_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    loan_type = db.Column(db.String(30), default='Home Loan')
    applicant_income = db.Column(db.Float, nullable=False)
    coapplicant_income = db.Column(db.Float, default=0)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_tenure = db.Column(db.Integer, nullable=False)
    credit_history = db.Column(db.Integer, nullable=False)
    cibil_score = db.Column(db.Integer, default=700)
    employment_status = db.Column(db.String(20), nullable=False)
    property_area = db.Column(db.String(20), nullable=False)
    education = db.Column(db.String(20), nullable=False)
    dependents = db.Column(db.String(5), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    married = db.Column(db.String(5), nullable=False)
    annual_income = db.Column(db.Float, default=0)
    existing_loans = db.Column(db.Integer, default=0)
    purpose = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='application', lazy=True)
    admin_decisions = db.relationship('AdminDecision', backref='application', lazy=True)


class Prediction(db.Model):
    __tablename__ = 'predictions'
    prediction_id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('loan_applications.application_id'), nullable=False)
    predicted_result = db.Column(db.String(20), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    model_used = db.Column(db.String(50))
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminDecision(db.Model):
    __tablename__ = 'admin_decisions'
    decision_id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('loan_applications.application_id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    admin_decision = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.Text)
    decision_date = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.relationship('User', foreign_keys=[admin_id])
