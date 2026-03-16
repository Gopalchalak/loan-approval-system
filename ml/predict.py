"""
Prediction Module - Applies preprocessing and ML model to generate loan predictions.
"""
import pickle
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config

def load_artifacts():
    artifacts = {}
    try:
        with open(Config.MODEL_PATH, 'rb') as f:
            artifacts['model'] = pickle.load(f)
        with open(Config.SCALER_PATH, 'rb') as f:
            artifacts['scaler'] = pickle.load(f)
        with open(Config.LABEL_ENCODERS_PATH, 'rb') as f:
            artifacts['label_encoders'] = pickle.load(f)
        with open(Config.MODEL_METRICS_PATH, 'rb') as f:
            data = pickle.load(f)
            artifacts['best_model_name'] = data['best_model_name']
            artifacts['feature_cols'] = data['feature_cols']
        return artifacts
    except FileNotFoundError:
        return None

def encode_categorical(value, encoder, default=0):
    try:
        return encoder.transform([str(value)])[0]
    except (ValueError, KeyError):
        return default

def predict_loan(form_data):
    """
    form_data: dict with keys:
        gender, married, dependents, education, self_employed,
        applicant_income, coapplicant_income, loan_amount, 
        loan_amount_term, credit_history, property_area
    Returns:
        dict with predicted_result, probability, risk_level, model_used
    """
    artifacts = load_artifacts()
    if not artifacts:
        return {
            'predicted_result': 'Error',
            'probability': 0,
            'risk_level': 'Unknown',
            'model_used': 'N/A',
            'error': 'Model not found. Please train the model first.'
        }
    
    model = artifacts['model']
    scaler = artifacts['scaler']
    label_encoders = artifacts['label_encoders']
    feature_cols = artifacts['feature_cols']
    model_name = artifacts['best_model_name']
    
    # Encode categoricals
    gender_enc = encode_categorical(form_data.get('gender', 'Male'), label_encoders['Gender'])
    married_enc = encode_categorical(form_data.get('married', 'No'), label_encoders['Married'])
    dep_enc = encode_categorical(form_data.get('dependents', '0'), label_encoders['Dependents'])
    edu_enc = encode_categorical(form_data.get('education', 'Graduate'), label_encoders['Education'])
    emp_enc = encode_categorical(form_data.get('self_employed', 'No'), label_encoders['Self_Employed'])
    prop_enc = encode_categorical(form_data.get('property_area', 'Urban'), label_encoders['Property_Area'])
    
    applicant_income = float(form_data.get('applicant_income', 5000))
    coapplicant_income = float(form_data.get('coapplicant_income', 0))
    loan_amount = float(form_data.get('loan_amount', 150))
    loan_amount_term = float(form_data.get('loan_amount_term', 360))
    credit_history = int(form_data.get('credit_history', 1))
    
    # Feature engineering
    total_income = applicant_income + coapplicant_income
    emi = loan_amount / (loan_amount_term + 1)
    balance_income = total_income - (emi * 1000)
    
    features = [
        gender_enc, married_enc, dep_enc, edu_enc, emp_enc,
        applicant_income, coapplicant_income, loan_amount, loan_amount_term,
        credit_history, prop_enc, total_income, emi, balance_income
    ]
    
    features_array = np.array(features).reshape(1, -1)
    features_scaled = scaler.transform(features_array)
    
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0][1]
    
    predicted_result = 'Approved' if prediction == 1 else 'Rejected'
    
    # Determine risk level
    if predicted_result == 'Approved':
        if probability >= 0.75:
            risk_level = 'Low Risk'
        elif probability >= 0.55:
            risk_level = 'Medium Risk'
        else:
            risk_level = 'High Risk'
    else:
        if probability <= 0.25:
            risk_level = 'High Risk'
        elif probability <= 0.45:
            risk_level = 'Medium Risk'
        else:
            risk_level = 'High Risk'
    
    return {
        'predicted_result': predicted_result,
        'probability': round(probability * 100, 2),
        'risk_level': risk_level,
        'model_used': model_name
    }

def get_model_metrics():
    try:
        with open(Config.MODEL_METRICS_PATH, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def get_all_models_predictions(form_data):
    """Run prediction with all trained models for comparison."""
    try:
        all_models_path = os.path.join(os.path.dirname(Config.MODEL_PATH), 'all_models.pkl')
        with open(all_models_path, 'rb') as f:
            all_models = pickle.load(f)
        with open(Config.SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        with open(Config.LABEL_ENCODERS_PATH, 'rb') as f:
            label_encoders = pickle.load(f)
        
        results = {}
        for model_name, model in all_models.items():
            pred = predict_loan(form_data)
            results[model_name] = pred
        return results
    except Exception:
        return {}
