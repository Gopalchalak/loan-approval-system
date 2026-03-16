import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.categorical_cols = ['Gender', 'Married', 'Dependents', 'Education',
                                  'Self_Employed', 'Property_Area']
        self.feature_cols = ['Gender', 'Married', 'Dependents', 'Education',
                             'Self_Employed', 'ApplicantIncome', 'CoapplicantIncome',
                             'LoanAmount', 'Loan_Amount_Term', 'Credit_History', 'Property_Area']

    def fit_transform(self, df):
        df = df.copy()
        df = self._handle_missing(df)
        df = self._encode_categoricals(df, fit=True)
        X = df[self.feature_cols]
        X_scaled = self.scaler.fit_transform(X)
        return pd.DataFrame(X_scaled, columns=self.feature_cols)

    def transform(self, df):
        df = df.copy()
        df = self._handle_missing(df)
        df = self._encode_categoricals(df, fit=False)
        X = df[self.feature_cols]
        X_scaled = self.scaler.transform(X)
        return pd.DataFrame(X_scaled, columns=self.feature_cols)

    def _handle_missing(self, df):
        df['Gender'].fillna('Male', inplace=True)
        df['Married'].fillna('Yes', inplace=True)
        df['Dependents'].fillna('0', inplace=True)
        df['Self_Employed'].fillna('No', inplace=True)
        df['LoanAmount'].fillna(df['LoanAmount'].median(), inplace=True)
        df['Loan_Amount_Term'].fillna(360.0, inplace=True)
        df['Credit_History'].fillna(1.0, inplace=True)
        df['Dependents'] = df['Dependents'].replace('3+', '3').astype(str)
        return df

    def _encode_categoricals(self, df, fit=True):
        for col in self.categorical_cols:
            if col not in df.columns:
                continue
            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                le = self.label_encoders.get(col)
                if le:
                    df[col] = df[col].astype(str)
                    known = set(le.classes_)
                    df[col] = df[col].apply(lambda x: x if x in known else le.classes_[0])
                    df[col] = le.transform(df[col])
        return df

    def transform_single(self, data_dict):
        """Transform a single loan application dict."""
        df = pd.DataFrame([data_dict])
        return self.transform(df)

    def save(self, scaler_path, encoder_path):
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoders, encoder_path)

    def load(self, scaler_path, encoder_path):
        self.scaler = joblib.load(scaler_path)
        self.label_encoders = joblib.load(encoder_path)
