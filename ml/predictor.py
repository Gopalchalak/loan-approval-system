import pickle, os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'trained_models', 'best_model.pkl')
RESULTS_PATH = os.path.join(BASE_DIR, 'trained_models', 'model_results.pkl')

_model = None
_results = None

def _load_model():
    global _model, _results
    if _model is None:
        with open(MODEL_PATH, 'rb') as f:
            _model = pickle.load(f)
    if _results is None:
        with open(RESULTS_PATH, 'rb') as f:
            _results = pickle.load(f)
    return _model, _results

def predict_loan(data: dict):
    model, _ = _load_model()
    cibil = int(data.get('cibil_score', 700))
    credit_history = 1 if cibil >= 650 else 0

    df = pd.DataFrame([{
        'Gender': data.get('gender', 'Male'),
        'Married': data.get('married', 'No'),
        'Dependents': str(data.get('dependents', '0')),
        'Education': data.get('education', 'Graduate'),
        'Self_Employed': data.get('employment_status', 'No'),
        'ApplicantIncome': float(data.get('applicant_income', 0)),
        'CoapplicantIncome': float(data.get('coapplicant_income', 0)),
        'LoanAmount': float(data.get('loan_amount', 0)),
        'Loan_Amount_Term': float(data.get('loan_tenure', 360)),
        'Credit_History': float(credit_history),
        'CIBIL_Score': float(cibil),
        'Property_Area': data.get('property_area', 'Urban'),
        'Loan_Type': data.get('loan_type', 'Home Loan'),
    }])

    proba = model.predict_proba(df)[0]
    pred = model.predict(df)[0]
    approval_prob = proba[1] * 100

    result = 'Approved' if pred == 1 else 'Rejected'

    if approval_prob >= 70:
        risk_level = 'Low Risk'
    elif approval_prob >= 45:
        risk_level = 'Medium Risk'
    else:
        risk_level = 'High Risk'

    # CIBIL-based override for very poor scores
    if cibil < 400:
        result = 'Rejected'
        risk_level = 'High Risk'
        approval_prob = min(approval_prob, 20)

    return {
        'result': result,
        'probability': round(approval_prob, 2),
        'risk_level': risk_level,
        'approved': bool(result == 'Approved'),
        'cibil_score': cibil
    }

def get_model_results():
    _, results = _load_model()
    return results
