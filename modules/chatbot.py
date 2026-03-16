RULES = [
    {
        'keywords': ['apply', 'application', 'how to apply', 'loan apply'],
        'response': (
            "📋 <b>How to Apply for a Loan:</b><br>"
            "1. Register or log in to your account.<br>"
            "2. Click <b>Apply for Loan</b> on your dashboard.<br>"
            "3. Fill in your income, loan amount, tenure, and other details.<br>"
            "4. Submit — our ML model will instantly predict your eligibility.<br>"
            "5. An admin will review and make the final decision."
        )
    },
    {
        'keywords': ['document', 'documents', 'required', 'what do i need'],
        'response': (
            "📄 <b>Required Documents:</b><br>"
            "• Valid Government ID (Aadhar / PAN / Passport)<br>"
            "• Income proof (salary slips / ITR)<br>"
            "• Bank statements (last 3 months)<br>"
            "• Address proof<br>"
            "• Property documents (if applicable)"
        )
    },
    {
        'keywords': ['approved', 'approval', 'what does approved mean'],
        'response': (
            "✅ <b>Loan Approved:</b><br>"
            "Your application meets our eligibility criteria. The loan amount will be processed and disbursed to your registered bank account within 3–5 business days."
        )
    },
    {
        'keywords': ['rejected', 'rejection', 'why rejected', 'declined'],
        'response': (
            "❌ <b>Loan Rejected:</b><br>"
            "Your application did not meet our current eligibility criteria. Common reasons include:<br>"
            "• Low credit history score<br>"
            "• Insufficient income relative to loan amount<br>"
            "• High existing debt<br>"
            "You may reapply after 3 months with improved credit history."
        )
    },
    {
        'keywords': ['prediction', 'ml', 'machine learning', 'how predict', 'algorithm'],
        'response': (
            "🤖 <b>About Our ML Prediction:</b><br>"
            "We use a <b>Random Forest</b> machine learning model trained on historical loan data.<br>"
            "It considers factors like income, loan amount, credit history, employment, and property area.<br>"
            "The model outputs an <b>approval probability (%)</b> and <b>risk level</b> (Low / Medium / High)."
        )
    },
    {
        'keywords': ['risk', 'risk level', 'low risk', 'medium risk', 'high risk'],
        'response': (
            "⚠️ <b>Risk Levels Explained:</b><br>"
            "• 🟢 <b>Low Risk</b>: Approval probability ≥ 80%. Strong application.<br>"
            "• 🟡 <b>Medium Risk</b>: Approval probability 60–79%. Review may be needed.<br>"
            "• 🔴 <b>High Risk</b>: Approval probability < 60%. Likely rejection."
        )
    },
    {
        'keywords': ['credit', 'cibil', 'credit score', 'credit history'],
        'response': (
            "💳 <b>Credit History / CIBIL:</b><br>"
            "Credit history is one of the most important factors.<br>"
            "• <b>1</b> = Good credit history (loan repayments on time)<br>"
            "• <b>0</b> = Poor credit history (defaults or missed payments)<br>"
            "A good CIBIL score (750+) significantly improves approval chances."
        )
    },
    {
        'keywords': ['tenure', 'loan term', 'repayment period', 'duration'],
        'response': (
            "📅 <b>Loan Tenure:</b><br>"
            "Loan tenure is the repayment period in months.<br>"
            "• Short tenure (12–60 months): Higher EMI, less interest overall.<br>"
            "• Long tenure (120–360 months): Lower EMI, more interest overall.<br>"
            "Common tenures: 120, 180, 240, 300, 360 months."
        )
    },
    {
        'keywords': ['income', 'salary', 'applicant income'],
        'response': (
            "💰 <b>Income Requirements:</b><br>"
            "Your income determines how much loan you can get.<br>"
            "• Minimum income: ₹15,000/month recommended<br>"
            "• Loan amount should generally not exceed 60× your monthly income<br>"
            "• Co-applicant income also improves eligibility"
        )
    },
    {
        'keywords': ['contact', 'help', 'support', 'phone', 'email'],
        'response': (
            "📞 <b>Contact Support:</b><br>"
            "• Email: support@loanpredict.com<br>"
            "• Phone: +91-800-LOAN-APP (1800-5626-277)<br>"
            "• Hours: Mon–Sat, 9AM–6PM IST<br>"
            "• Or chat with us here anytime!"
        )
    },
    {
        'keywords': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'greet'],
        'response': (
            "👋 Hello! Welcome to <b>LoanPredict AI</b>!<br>"
            "I'm your virtual assistant. Ask me about:<br>"
            "• How to apply for a loan<br>"
            "• Required documents<br>"
            "• Approval / Rejection status<br>"
            "• Credit history & risk levels<br>"
            "How can I help you today?"
        )
    },
]

DEFAULT_RESPONSE = (
    "🤔 I'm not sure I understood that. Try asking about:<br>"
    "• <i>How to apply</i><br>"
    "• <i>Required documents</i><br>"
    "• <i>What does approved/rejected mean</i><br>"
    "• <i>Risk levels</i><br>"
    "• <i>Credit history</i><br>"
    "• <i>Contact support</i>"
)

def get_response(user_message):
    msg = user_message.lower().strip()
    for rule in RULES:
        for kw in rule['keywords']:
            if kw in msg:
                return rule['response']
    return DEFAULT_RESPONSE
