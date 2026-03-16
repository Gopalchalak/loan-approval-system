import joblib
import numpy as np
import pandas as pd
import os
from .preprocessing import DataPreprocessor

class LoanPredictor:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.model = None
        self.preprocessor = DataPreprocessor()
        self._load()

    def _load(self):
        model_path = os.path.join(self.model_dir, 'best_model.pkl')
        scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        encoder_path = os.path.join(self.model_dir, 'encoders.pkl')
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.preprocessor.load(scaler_path, encoder_path)

    def predict(self, application_data):
        """
        application_data: dict with keys matching feature columns
        Returns: dict with result, probability, risk_level
        """
        if self.model is None:
            return None

        X = self.preprocessor.transform_single(application_data)
        pred = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0]

        # pred=1 means Approved (Y), pred=0 means Rejected (N)
        approved = bool(pred == 1)
        approval_prob = round(float(proba[1]) * 100, 1)

        if approved:
            if approval_prob >= 80:
                risk_level = 'Low Risk'
            elif approval_prob >= 60:
                risk_level = 'Medium Risk'
            else:
                risk_level = 'High Risk'
        else:
            if approval_prob <= 20:
                risk_level = 'High Risk'
            elif approval_prob <= 40:
                risk_level = 'Medium Risk'
            else:
                risk_level = 'High Risk'

        return {
            'result': 'Approved' if approved else 'Rejected',
            'approved': approved,
            'probability': approval_prob,
            'risk_level': risk_level
        }
