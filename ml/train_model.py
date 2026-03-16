import pandas as pd
import numpy as np
import pickle, os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def train_and_save():
    df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'loan_data.csv'))
    print(f"Loaded {len(df)} records | Approval: {(df['Loan_Status']=='Y').mean():.1%}")

    df['Loan_Status'] = df['Loan_Status'].map({'Y': 1, 'N': 0})
    df.dropna(subset=['Loan_Status'], inplace=True)

    X = df.drop('Loan_Status', axis=1)
    y = df['Loan_Status']

    cat_features = ['Gender','Married','Dependents','Education','Self_Employed','Property_Area','Loan_Type']
    num_features = ['ApplicantIncome','CoapplicantIncome','LoanAmount','Loan_Amount_Term','Credit_History','CIBIL_Score']

    # Only use columns that exist
    cat_features = [c for c in cat_features if c in X.columns]
    num_features = [c for c in num_features if c in X.columns]

    num_pipeline = Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])
    cat_pipeline = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')),
                              ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    preprocessor = ColumnTransformer([('num', num_pipeline, num_features), ('cat', cat_pipeline, cat_features)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
        'Decision Tree': DecisionTreeClassifier(max_depth=7, random_state=42, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, class_weight='balanced'),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }

    results = {}
    best_f1 = 0
    best_model_name = ''
    best_pipeline = None

    for name, model in models.items():
        pipe = Pipeline([('preprocessor', preprocessor), ('classifier', model)])
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {'accuracy': round(acc,4), 'precision': round(prec,4),
                         'recall': round(rec,4), 'f1_score': round(f1,4), 'confusion_matrix': cm}
        print(f"{name}: Acc={acc:.4f}, Precision={prec:.4f}, Recall={rec:.4f}, F1={f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipeline = pipe

    print(f"\nBest model: {best_model_name} (F1={best_f1:.4f})")
    os.makedirs(os.path.join(BASE_DIR, 'trained_models'), exist_ok=True)
    with open(os.path.join(BASE_DIR, 'trained_models', 'best_model.pkl'), 'wb') as f:
        pickle.dump(best_pipeline, f)
    with open(os.path.join(BASE_DIR, 'trained_models', 'model_results.pkl'), 'wb') as f:
        pickle.dump({'results': results, 'best_model': best_model_name}, f)
    print("Saved!")
    return results, best_model_name

if __name__ == '__main__':
    train_and_save()
