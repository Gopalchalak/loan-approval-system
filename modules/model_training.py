import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import json
from .preprocessing import DataPreprocessor

def train_models(train_path, model_dir):
    os.makedirs(model_dir, exist_ok=True)
    df = pd.read_csv(train_path)

    # Encode target
    le_target = LabelEncoder()
    df['Loan_Status_Enc'] = le_target.fit_transform(df['Loan_Status'])  # N=0, Y=1

    preprocessor = DataPreprocessor()
    X = preprocessor.fit_transform(df)
    y = df['Loan_Status_Enc']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
    }

    results = {}
    best_model = None
    best_acc = 0
    best_name = ''

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            'accuracy': round(acc * 100, 2),
            'precision': round(prec * 100, 2),
            'recall': round(rec * 100, 2),
            'f1_score': round(f1 * 100, 2),
            'confusion_matrix': cm
        }

        if acc > best_acc:
            best_acc = acc
            best_model = model
            best_name = name

    # Save best model and preprocessor
    joblib.dump(best_model, os.path.join(model_dir, 'best_model.pkl'))
    preprocessor.save(
        os.path.join(model_dir, 'scaler.pkl'),
        os.path.join(model_dir, 'encoders.pkl')
    )

    results['best_model'] = best_name
    results['classes'] = le_target.classes_.tolist()

    with open(os.path.join(model_dir, 'eval_results.json'), 'w') as f:
        json.dump(results, f)

    return results

def load_evaluation_results(model_dir):
    path = os.path.join(model_dir, 'eval_results.json')
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None
