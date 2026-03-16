import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

np.random.seed(42)
n = 2000

gender = np.random.choice(['Male', 'Female'], n, p=[0.75, 0.25])
married = np.random.choice(['Yes', 'No'], n, p=[0.60, 0.40])
dependents = np.random.choice(['0', '1', '2', '3+'], n, p=[0.50, 0.20, 0.18, 0.12])
education = np.random.choice(['Graduate', 'Not Graduate'], n, p=[0.72, 0.28])
self_employed = np.random.choice(['Yes', 'No'], n, p=[0.18, 0.82])
credit_history = np.random.choice([1, 0], n, p=[0.65, 0.35])
property_area = np.random.choice(['Urban', 'Semiurban', 'Rural'], n, p=[0.35, 0.38, 0.27])
loan_type = np.random.choice(['Home Loan','Car Loan','Education Loan','Personal Loan','Business Loan'], n,
                              p=[0.30, 0.20, 0.18, 0.20, 0.12])

applicant_income = np.random.lognormal(8.3, 0.7, n).astype(int)
applicant_income = np.clip(applicant_income, 1500, 80000)

coapplicant_income = np.where(
    married == 'Yes',
    np.random.lognormal(7.0, 0.9, n).astype(int),
    0
)
coapplicant_income = np.clip(coapplicant_income, 0, 50000)

loan_amount = (applicant_income * np.random.uniform(0.8, 6.0, n) / 1000).astype(int)
loan_amount = np.clip(loan_amount, 10, 1000)

loan_tenure = np.random.choice([12,24,36,60,84,120,180,240,300,360,480], n,
    p=[0.03,0.04,0.05,0.07,0.06,0.08,0.10,0.08,0.07,0.38,0.04])

cibil_score = np.where(credit_history == 1,
    np.random.randint(650, 900, n),
    np.random.randint(300, 649, n))

score = np.zeros(n)
score += (cibil_score >= 750) * 0.35
score += (cibil_score >= 650) * 0.10
score += (applicant_income > 6000) * 0.12
score += (applicant_income > 3000) * 0.06
score += (education == 'Graduate') * 0.08
score += (self_employed == 'No') * 0.07
score += (loan_amount < 300) * 0.08
score += (loan_amount < 150) * 0.05
score += (property_area == 'Semiurban') * 0.05
score += (married == 'Yes') * 0.04
score += (coapplicant_income > 2000) * 0.05
score -= (dependents == '3+') * 0.06
score -= (loan_amount > 600) * 0.08
score -= (self_employed == 'Yes') * 0.04
score += np.random.uniform(-0.10, 0.10, n)
score = np.clip(score, 0, 1)

threshold = np.percentile(score, 45)
loan_status = np.where(score > threshold, 'Y', 'N')

df = pd.DataFrame({
    'Gender': gender, 'Married': married, 'Dependents': dependents,
    'Education': education, 'Self_Employed': self_employed,
    'ApplicantIncome': applicant_income, 'CoapplicantIncome': coapplicant_income,
    'LoanAmount': loan_amount, 'Loan_Amount_Term': loan_tenure,
    'Credit_History': credit_history, 'CIBIL_Score': cibil_score,
    'Property_Area': property_area, 'Loan_Type': loan_type,
    'Loan_Status': loan_status
})

for col in ['Gender','Married','Dependents','Self_Employed','LoanAmount','Loan_Amount_Term','Credit_History']:
    mask = np.random.random(n) < 0.025
    df.loc[mask, col] = np.nan

os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'trained_models'), exist_ok=True)

save_path = os.path.join(BASE_DIR, 'data', 'loan_data.csv')
df.to_csv(save_path, index=False)
print(f"Dataset saved to {save_path}")
print(df['Loan_Status'].value_counts())
print(f"Approval rate: {(df['Loan_Status']=='Y').mean():.1%}")