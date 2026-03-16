import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os

def approval_vs_rejection_chart(applications):
    approved = sum(1 for a in applications if a.status == 'Approved')
    rejected = sum(1 for a in applications if a.status == 'Rejected')
    pending = sum(1 for a in applications if a.status == 'Pending')

    fig = go.Figure(data=[go.Pie(
        labels=['Approved', 'Rejected', 'Pending'],
        values=[approved, rejected, pending],
        hole=0.45,
        marker_colors=['#22c55e', '#ef4444', '#f59e0b'],
        textinfo='label+percent+value'
    )])
    fig.update_layout(
        title='Loan Approval vs Rejection',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1e293b'),
        showlegend=True
    )
    return json.loads(fig.to_json())

def credit_history_impact_chart(applications, predictions):
    pred_map = {p.application_id: p for p in predictions}
    credit_approved = {'Good (1)': 0, 'Poor (0)': 0}
    credit_rejected = {'Good (1)': 0, 'Poor (0)': 0}

    for app in applications:
        credit = 'Good (1)' if app.credit_history == 1 else 'Poor (0)'
        pred = pred_map.get(app.id)
        if pred:
            if pred.predicted_result == 'Approved':
                credit_approved[credit] += 1
            else:
                credit_rejected[credit] += 1

    fig = go.Figure(data=[
        go.Bar(name='Approved', x=list(credit_approved.keys()),
               y=list(credit_approved.values()), marker_color='#22c55e'),
        go.Bar(name='Rejected', x=list(credit_rejected.keys()),
               y=list(credit_rejected.values()), marker_color='#ef4444'),
    ])
    fig.update_layout(
        barmode='group',
        title='Credit History Impact on Loan Approval',
        xaxis_title='Credit History',
        yaxis_title='Number of Applications',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1e293b')
    )
    return json.loads(fig.to_json())

def loan_amount_distribution_chart(applications):
    amounts = [a.loan_amount for a in applications if a.loan_amount]
    if not amounts:
        amounts = [0]
    fig = go.Figure(data=[go.Histogram(
        x=amounts,
        nbinsx=20,
        marker_color='#6366f1',
        opacity=0.8
    )])
    fig.update_layout(
        title='Loan Amount Distribution',
        xaxis_title='Loan Amount (₹ Thousands)',
        yaxis_title='Number of Applications',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1e293b')
    )
    return json.loads(fig.to_json())

def model_comparison_chart(eval_results):
    models = ['Logistic Regression', 'Decision Tree', 'Random Forest']
    metrics = ['accuracy', 'precision', 'recall', 'f1_score']
    labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    colors = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444']

    fig = go.Figure()
    for i, metric in enumerate(metrics):
        vals = [eval_results.get(m, {}).get(metric, 0) for m in models]
        fig.add_trace(go.Bar(
            name=labels[i],
            x=models,
            y=vals,
            marker_color=colors[i]
        ))

    fig.update_layout(
        barmode='group',
        title='ML Model Performance Comparison (%)',
        xaxis_title='Model',
        yaxis_title='Score (%)',
        yaxis=dict(range=[0, 110]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1e293b')
    )
    return json.loads(fig.to_json())

def income_vs_loan_scatter(applications):
    incomes = [a.income for a in applications if a.income]
    amounts = [a.loan_amount for a in applications if a.loan_amount]
    statuses = [a.status for a in applications if a.income and a.loan_amount]
    colors = {'Approved': '#22c55e', 'Rejected': '#ef4444', 'Pending': '#f59e0b'}

    fig = go.Figure()
    for status in ['Approved', 'Rejected', 'Pending']:
        idxs = [i for i, s in enumerate(statuses) if s == status]
        fig.add_trace(go.Scatter(
            x=[incomes[i] for i in idxs],
            y=[amounts[i] for i in idxs],
            mode='markers',
            name=status,
            marker=dict(color=colors[status], size=8, opacity=0.7)
        ))

    fig.update_layout(
        title='Income vs Loan Amount',
        xaxis_title='Applicant Income (₹)',
        yaxis_title='Loan Amount (₹ Thousands)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1e293b')
    )
    return json.loads(fig.to_json())

def monthly_applications_chart(applications):
    from collections import defaultdict
    monthly = defaultdict(int)
    for app in applications:
        if app.created_at:
            key = app.created_at.strftime('%Y-%m')
            monthly[key] += 1

    sorted_keys = sorted(monthly.keys())
    fig = go.Figure(data=go.Scatter(
        x=sorted_keys,
        y=[monthly[k] for k in sorted_keys],
        mode='lines+markers',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title='Monthly Loan Applications',
        xaxis_title='Month',
        yaxis_title='Applications',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1e293b')
    )
    return json.loads(fig.to_json())
