# LoanSense AI - Loan Approval / Credit Risk Prediction System

## Overview
A complete Machine Learning Web Application that predicts loan approval using trained ML models.

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run
```bash
python run.py
```
Visit: http://localhost:5000

## Login Credentials
- **Admin:** admin@loan.com / Admin@123
- **Demo User:** rahul@demo.com / Demo@123

## 10 Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | User Module | Registration, login, profile management |
| 2 | Loan Application | 12-field loan form with validation |
| 3 | Data Preprocessing | Imputation, encoding, StandardScaler pipeline |
| 4 | ML Model | Logistic Regression, Decision Tree, Random Forest |
| 5 | Prediction & Decision | Probability %, risk level (Low/Medium/High) |
| 6 | Database | SQLite with SQLAlchemy ORM (5 tables) |
| 7 | Admin Panel | Review applications, approve/reject manually |
| 8 | Model Evaluation | Accuracy, Precision, Recall, F1, Confusion Matrix |
| 9 | Chatbot | Rule-based chatbot with 15+ question patterns |
| 10 | Analytics | Charts: approval rate, credit impact, risk distribution |

## Project Structure
```
loan_system/
├── app.py              # Flask application factory
├── config.py           # Configuration
├── extensions.py       # Flask extensions (db, login_manager)
├── models.py           # SQLAlchemy database models
├── run.py              # Entry point
├── requirements.txt
├── ml/
│   ├── generate_data.py    # Synthetic dataset generator
│   ├── train_model.py      # ML training (3 models)
│   └── predictor.py        # Prediction module
├── routes/
│   ├── auth.py         # Login/register/logout
│   ├── user.py         # User dashboard, apply, results
│   ├── admin.py        # Admin panel
│   ├── chatbot.py      # Rule-based chatbot API
│   └── analytics.py    # Analytics API + dashboard
├── templates/          # Jinja2 HTML templates
├── data/               # loan_data.csv (1000 records)
└── trained_models/     # Saved ML models (pkl)
```

## ML Models Performance
- Logistic Regression: ~97.5%
- Decision Tree: ~97.5%
- **Random Forest: ~98.0% (Best)**

## Database Tables
- users, loan_applications, predictions, admin_decisions, model_metrics
