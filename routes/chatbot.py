from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

# Keyword-based matching with multiple patterns per topic
QA = [
    {
        'keywords': ['document', 'required', 'need', 'paper', 'submit', 'proof'],
        'answer': '📄 <strong>Documents Required for Loan Application:</strong><br><br>'
                  '• <strong>Identity Proof:</strong> Aadhaar Card, PAN Card, Passport or Voter ID<br>'
                  '• <strong>Address Proof:</strong> Utility bill, Rent agreement or Passport<br>'
                  '• <strong>Income Proof:</strong> Last 3 months salary slips or ITR for self-employed<br>'
                  '• <strong>Bank Statements:</strong> Last 6 months bank statements<br>'
                  '• <strong>Employment Proof:</strong> Offer letter or employment certificate<br>'
                  '• <strong>Property Documents:</strong> For home/mortgage loans (sale deed, NOC)<br>'
                  '• <strong>CIBIL Report:</strong> Credit score report (auto-checked via CIBIL score entry)<br>'
                  '• <strong>Photographs:</strong> Recent passport-size photos<br><br>'
                  '<em>All documents must be self-attested copies.</em>'
    },
    {
        'keywords': ['apply', 'application', 'process', 'how to', 'steps', 'procedure', 'start'],
        'answer': '🏦 <strong>Loan Application Process:</strong><br><br>'
                  '<strong>Step 1:</strong> Register/Login to your account<br>'
                  '<strong>Step 2:</strong> Click "Apply for Loan" in the sidebar<br>'
                  '<strong>Step 3:</strong> Select your loan type (Home, Car, Education, etc.)<br>'
                  '<strong>Step 4:</strong> Fill in income, loan amount and personal details<br>'
                  '<strong>Step 5:</strong> Enter your CIBIL score and other financial info<br>'
                  '<strong>Step 6:</strong> Submit — our AI model gives instant prediction<br>'
                  '<strong>Step 7:</strong> Admin reviews and gives final approval/rejection<br><br>'
                  '<em>The whole process takes less than 5 minutes!</em>'
    },
    {
        'keywords': ['cibil', 'credit score', 'credit history', 'score', 'credit report'],
        'answer': '📊 <strong>CIBIL Score Explained:</strong><br><br>'
                  '• <strong>750 - 900:</strong> Excellent ✅ — Very high approval chance<br>'
                  '• <strong>700 - 749:</strong> Good ✅ — Good approval chance<br>'
                  '• <strong>650 - 699:</strong> Fair ⚠️ — Moderate chance, may need conditions<br>'
                  '• <strong>600 - 649:</strong> Poor ⚠️ — Low chance, higher interest rate<br>'
                  '• <strong>300 - 599:</strong> Very Poor ❌ — Very unlikely to be approved<br><br>'
                  'Your CIBIL score is the <strong>most important factor</strong> in loan approval. '
                  'Pay bills on time and reduce debts to improve it.'
    },
    {
        'keywords': ['approved', 'approve', 'approval', 'eligible', 'eligibility', 'qualify'],
        'answer': '✅ <strong>Loan Approval Factors:</strong><br><br>'
                  '• <strong>CIBIL Score:</strong> 750+ greatly improves chances<br>'
                  '• <strong>Income:</strong> Higher stable income = better approval<br>'
                  '• <strong>Loan Amount:</strong> Should be within 3-5x your monthly income<br>'
                  '• <strong>Employment:</strong> Salaried employees have slightly better rates<br>'
                  '• <strong>Property Area:</strong> Semiurban areas have favorable rates<br>'
                  '• <strong>Education:</strong> Graduate applicants score higher<br>'
                  '• <strong>Co-applicant:</strong> Adding income improves eligibility<br><br>'
                  'Our AI model analyzes all these factors to give an <strong>instant prediction with probability %</strong>.'
    },
    {
        'keywords': ['reject', 'rejected', 'denial', 'denied', 'decline', 'not approved', 'why rejected'],
        'answer': '❌ <strong>Common Reasons for Loan Rejection:</strong><br><br>'
                  '• Low CIBIL score (below 650)<br>'
                  '• Insufficient income relative to loan amount<br>'
                  '• Too many existing loans or high debt-to-income ratio<br>'
                  '• Unstable employment history<br>'
                  '• Incomplete or incorrect documentation<br>'
                  '• Poor repayment history on previous loans<br>'
                  '• Loan amount too high compared to income<br><br>'
                  '<strong>To improve your chances:</strong> Improve CIBIL score, reduce existing debts, add a co-applicant, or reduce the loan amount.'
    },
    {
        'keywords': ['risk', 'risk level', 'low risk', 'medium risk', 'high risk'],
        'answer': '🛡️ <strong>Risk Level Explained:</strong><br><br>'
                  '• <strong>🟢 Low Risk (70%+ probability):</strong> Strong financial profile, very likely to be approved<br>'
                  '• <strong>🟡 Medium Risk (45-70%):</strong> Borderline case, admin will review carefully<br>'
                  '• <strong>🔴 High Risk (below 45%):</strong> Weak profile, likely to be rejected<br><br>'
                  'Risk level is calculated by our <strong>Random Forest ML model</strong> trained on thousands of loan records.'
    },
    {
        'keywords': ['loan type', 'home loan', 'car loan', 'education loan', 'personal loan', 'business loan', 'types of loan'],
        'answer': '🏠 <strong>Types of Loans Available:</strong><br><br>'
                  '• <strong>🏠 Home Loan:</strong> For purchasing or constructing a house. Up to ₹10 Lakhs, tenure up to 30 years<br>'
                  '• <strong>🚗 Car Loan:</strong> For new or used vehicles. Up to ₹10 Lakhs, tenure up to 7 years<br>'
                  '• <strong>🎓 Education Loan:</strong> For higher studies in India or abroad. Up to ₹10 Lakhs<br>'
                  '• <strong>💼 Personal Loan:</strong> For any personal need. Up to ₹10 Lakhs, shorter tenure<br>'
                  '• <strong>🏢 Business Loan:</strong> For business expansion or working capital<br><br>'
                  'Select your loan type in the application form to get started!'
    },
    {
        'keywords': ['amount', 'loan amount', 'how much', 'maximum', 'limit', 'lakh', '10 lakh'],
        'answer': '💰 <strong>Loan Amount Details:</strong><br><br>'
                  '• Maximum loan amount: <strong>₹10,00,000 (10 Lakhs)</strong><br>'
                  '• Minimum loan amount: <strong>₹10,000</strong><br>'
                  '• Recommended: Keep loan amount within <strong>3-5x your monthly income</strong><br>'
                  '• Higher amounts require better CIBIL score and higher income<br><br>'
                  'Enter the loan amount in <strong>thousands (₹)</strong> in the application form.<br>'
                  'For example: enter 500 for ₹5,00,000 (5 Lakhs).'
    },
    {
        'keywords': ['tenure', 'duration', 'period', 'months', 'years', 'repayment', 'emi'],
        'answer': '📅 <strong>Loan Tenure Options:</strong><br><br>'
                  '• <strong>Home Loan:</strong> 12 to 360 months (1 to 30 years)<br>'
                  '• <strong>Car Loan:</strong> 12 to 84 months (1 to 7 years)<br>'
                  '• <strong>Education Loan:</strong> 12 to 120 months (1 to 10 years)<br>'
                  '• <strong>Personal Loan:</strong> 12 to 60 months (1 to 5 years)<br>'
                  '• <strong>Business Loan:</strong> 12 to 84 months<br><br>'
                  '<strong>Tip:</strong> Longer tenure = lower EMI but more total interest paid. Choose wisely!'
    },
    {
        'keywords': ['status', 'check', 'track', 'application status', 'my application', 'where'],
        'answer': '🔍 <strong>How to Check Application Status:</strong><br><br>'
                  '1. Go to <strong>"My Applications"</strong> in the sidebar<br>'
                  '2. Your application status will show as:<br>'
                  '   • 🟡 <strong>Pending</strong> — Under admin review<br>'
                  '   • 🟢 <strong>Approved</strong> — Loan approved by admin<br>'
                  '   • 🔴 <strong>Rejected</strong> — Loan rejected by admin<br>'
                  '3. Click <strong>"View"</strong> on any application to see full details and ML prediction result'
    },
    {
        'keywords': ['prediction', 'ai', 'machine learning', 'model', 'how does it work', 'algorithm'],
        'answer': '🤖 <strong>How Our AI Prediction Works:</strong><br><br>'
                  '• We use a <strong>Random Forest</strong> machine learning model<br>'
                  '• Trained on <strong>2000+ real loan applications</strong><br>'
                  '• Analyzes 12+ factors: income, CIBIL, loan type, employment, education, etc.<br>'
                  '• Gives <strong>instant approval probability (%)</strong><br>'
                  '• Classifies risk as Low / Medium / High<br>'
                  '• Model accuracy: <strong>~89%</strong><br><br>'
                  '<em>Note: AI prediction is a recommendation. Final decision is made by the admin.</em>'
    },
    {
        'keywords': ['interest', 'interest rate', 'rate', 'charges', 'fee'],
        'answer': '💳 <strong>Interest Rates (Indicative):</strong><br><br>'
                  '• <strong>Home Loan:</strong> 8.5% - 10.5% per annum<br>'
                  '• <strong>Car Loan:</strong> 9.0% - 13.0% per annum<br>'
                  '• <strong>Education Loan:</strong> 8.0% - 12.0% per annum<br>'
                  '• <strong>Personal Loan:</strong> 12.0% - 18.0% per annum<br>'
                  '• <strong>Business Loan:</strong> 11.0% - 16.0% per annum<br><br>'
                  'Rates depend on your CIBIL score, income, and loan tenure. Better CIBIL = lower interest rate!'
    },
    {
        'keywords': ['improve', 'increase', 'better', 'tips', 'chance', 'how to improve'],
        'answer': '💡 <strong>Tips to Improve Loan Approval Chances:</strong><br><br>'
                  '1. ✅ Maintain CIBIL score above 750<br>'
                  '2. ✅ Pay all existing EMIs and credit card bills on time<br>'
                  '3. ✅ Keep loan amount within 3x your monthly income<br>'
                  '4. ✅ Add a co-applicant (spouse/parent) to boost income<br>'
                  '5. ✅ Clear existing loans before applying<br>'
                  '6. ✅ Apply for semiurban or urban property loans<br>'
                  '7. ✅ Choose longer tenure to reduce EMI burden<br>'
                  '8. ✅ Be a salaried employee (more stable for banks)'
    },
    {
        'keywords': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greet', 'start'],
        'answer': '👋 <strong>Hello! Welcome to LoanSense AI!</strong><br><br>'
                  'I\'m <strong>LoanBot</strong>, your personal loan assistant. I can help you with:<br><br>'
                  '• 📋 Loan application process<br>'
                  '• 📄 Required documents<br>'
                  '• 📊 CIBIL score guidance<br>'
                  '• 💰 Loan types and amounts<br>'
                  '• ❓ Approval/rejection reasons<br><br>'
                  'How can I help you today?'
    },
    {
        'keywords': ['thank', 'thanks', 'thank you', 'okay', 'ok', 'great', 'nice'],
        'answer': '😊 You\'re welcome! Feel free to ask me anything else about loans. I\'m here to help! 🏦'
    },
    {
        'keywords': ['help', 'option', 'what can you do', 'menu'],
        'answer': '🤖 <strong>I can help you with:</strong><br><br>'
                  '1. 📋 <strong>Loan application process</strong> — Ask "How to apply?"<br>'
                  '2. 📄 <strong>Required documents</strong> — Ask "What documents are needed?"<br>'
                  '3. 📊 <strong>CIBIL score</strong> — Ask "What is CIBIL score?"<br>'
                  '4. 🏠 <strong>Loan types</strong> — Ask "What types of loans are available?"<br>'
                  '5. 💰 <strong>Loan amount</strong> — Ask "What is the maximum loan amount?"<br>'
                  '6. 📅 <strong>Tenure</strong> — Ask "What are tenure options?"<br>'
                  '7. ✅ <strong>Approval tips</strong> — Ask "How to improve approval chances?"<br>'
                  '8. ❌ <strong>Rejection reasons</strong> — Ask "Why was my loan rejected?"<br>'
                  '9. 🛡️ <strong>Risk levels</strong> — Ask "What does risk level mean?"<br>'
                  '10. 🔍 <strong>Application status</strong> — Ask "How to check status?"'
    },
]

DEFAULT = ('🤔 I didn\'t quite understand that. Here are some things you can ask me:<br><br>'
           '• "What documents are required?"<br>'
           '• "How do I apply for a loan?"<br>'
           '• "What is CIBIL score?"<br>'
           '• "What types of loans are available?"<br>'
           '• "Why was my loan rejected?"<br>'
           '• "How to improve my approval chances?"<br><br>'
           'Type <strong>"help"</strong> to see all topics!')

def get_response(message: str) -> str:
    msg = message.lower().strip()
    for qa in QA:
        if any(kw in msg for kw in qa['keywords']):
            return qa['answer']
    return DEFAULT

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = get_response(user_message)
    return jsonify({'response': response, 'status': 'ok'})
