from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print(" LoanSense AI - Loan Approval Prediction System")
    print("="*60)
    print(" URL: http://localhost:5000")
    print(" Admin Login: admin@loan.com / Admin@123")
    print(" Demo User:   rahul@demo.com / Demo@123")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
