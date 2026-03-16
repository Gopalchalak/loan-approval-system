"""
Analytics & Visualization Module
Generates interactive Plotly charts for the dashboard.
"""
import plotly.graph_objects as go
import plotly.express as px
import json
import pickle
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config

COLORS = {
    'approved': '#22c55e',
    'rejected': '#ef4444',
    'low_risk': '#22c55e',
    'medium_risk': '#f59e0b',
    'high_risk': '#ef4444',
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'bg': '#0f172a',
    'card': '#1e293b',
    'text': '#e2e8f0',
    'grid': '#334155'
}

LAYOUT_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans, sans-serif', color=COLORS['text'], size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['text']))
)

def fig_to_json(fig):
    return json.loads(fig.to_json())

def approval_donut_chart(data):
    ml_approved = data.get('ml_approved', 0)
    ml_rejected = data.get('ml_rejected', 0)
    total = ml_approved + ml_rejected
    
    if total == 0:
        ml_approved, ml_rejected, total = 3, 2, 5  # Demo data
    
    fig = go.Figure(go.Pie(
        labels=['Approved', 'Rejected'],
        values=[ml_approved, ml_rejected],
        hole=0.65,
        marker=dict(colors=[COLORS['approved'], COLORS['rejected']],
                    line=dict(color='#0f172a', width=3)),
        textinfo='label+percent',
        textfont=dict(size=13, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>'
    ))
    
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='ML Prediction Distribution', font=dict(size=15, color=COLORS['text'])),
        annotations=[dict(
            text=f'<b>{total}</b><br>Total',
            x=0.5, y=0.5, font=dict(size=16, color=COLORS['text']),
            showarrow=False
        )]
    )
    return fig_to_json(fig)

def credit_history_chart(data):
    credit_data = data.get('credit_history_data', [])
    
    if not credit_data:
        credit_data = [
            {'credit_history': 1, 'predicted_result': 'Approved', 'count': 320},
            {'credit_history': 1, 'predicted_result': 'Rejected', 'count': 80},
            {'credit_history': 0, 'predicted_result': 'Approved', 'count': 30},
            {'credit_history': 0, 'predicted_result': 'Rejected', 'count': 70},
        ]
    
    groups = {}
    for row in credit_data:
        ch = 'Good (1)' if row['credit_history'] == 1 else 'Bad (0)'
        result = row['predicted_result']
        if ch not in groups:
            groups[ch] = {'Approved': 0, 'Rejected': 0}
        groups[ch][result] = groups[ch].get(result, 0) + row['count']
    
    cats = list(groups.keys())
    approved_vals = [groups[c].get('Approved', 0) for c in cats]
    rejected_vals = [groups[c].get('Rejected', 0) for c in cats]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Approved', x=cats, y=approved_vals,
                         marker_color=COLORS['approved'],
                         hovertemplate='<b>%{x}</b><br>Approved: %{y}<extra></extra>'))
    fig.add_trace(go.Bar(name='Rejected', x=cats, y=rejected_vals,
                         marker_color=COLORS['rejected'],
                         hovertemplate='<b>%{x}</b><br>Rejected: %{y}<extra></extra>'))
    
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Credit History Impact on Approval', font=dict(size=15, color=COLORS['text'])),
        barmode='group',
        xaxis=dict(title='Credit History', gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
        yaxis=dict(title='Number of Applications', gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
    )
    return fig_to_json(fig)

def loan_amount_histogram(data):
    amounts = data.get('loan_amounts', [])
    
    if not amounts:
        import numpy as np
        np.random.seed(42)
        amounts = np.random.lognormal(5, 0.6, 200).clip(10, 700).tolist()
    
    fig = go.Figure(go.Histogram(
        x=amounts,
        nbinsx=30,
        marker=dict(color=COLORS['primary'], opacity=0.85,
                    line=dict(color='#0f172a', width=1)),
        hovertemplate='Loan Amount: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Loan Amount Distribution (₹ Thousands)', font=dict(size=15, color=COLORS['text'])),
        xaxis=dict(title='Loan Amount (₹000)', gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
        yaxis=dict(title='Number of Applications', gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
    )
    return fig_to_json(fig)

def model_accuracy_chart():
    try:
        with open(Config.MODEL_METRICS_PATH, 'rb') as f:
            data = pickle.load(f)
        metrics = data['metrics']
        best = data['best_model_name']
    except Exception:
        metrics = {
            'Logistic Regression': {'accuracy': 0.81, 'precision': 0.83, 'recall': 0.88, 'f1_score': 0.85},
            'Decision Tree': {'accuracy': 0.78, 'precision': 0.80, 'recall': 0.85, 'f1_score': 0.82},
            'Random Forest': {'accuracy': 0.87, 'precision': 0.89, 'recall': 0.91, 'f1_score': 0.90}
        }
        best = 'Random Forest'
    
    models = list(metrics.keys())
    metric_names = ['accuracy', 'precision', 'recall', 'f1_score']
    labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
    palette = [COLORS['primary'], COLORS['secondary'], COLORS['approved'], '#f59e0b']
    
    fig = go.Figure()
    for i, (metric, label, color) in enumerate(zip(metric_names, labels, palette)):
        vals = [metrics[m][metric] * 100 for m in models]
        display_models = [f'⭐ {m}' if m == best else m for m in models]
        fig.add_trace(go.Bar(
            name=label, x=display_models, y=vals,
            marker_color=color, opacity=0.9,
            hovertemplate=f'<b>%{{x}}</b><br>{label}: %{{y:.2f}}%<extra></extra>'
        ))
    
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Model Performance Comparison', font=dict(size=15, color=COLORS['text'])),
        barmode='group',
        xaxis=dict(gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
        yaxis=dict(title='Score (%)', range=[0, 105], gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
    )
    return fig_to_json(fig)

def risk_level_chart(data):
    risk_dist = data.get('risk_distribution', {})
    
    if not risk_dist:
        risk_dist = {'Low Risk': 45, 'Medium Risk': 30, 'High Risk': 25}
    
    labels = list(risk_dist.keys())
    values = list(risk_dist.values())
    colors = []
    for l in labels:
        if 'Low' in l:
            colors.append(COLORS['low_risk'])
        elif 'Medium' in l:
            colors.append(COLORS['medium_risk'])
        else:
            colors.append(COLORS['high_risk'])
    
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors, line=dict(color='#0f172a', width=3)),
        textinfo='label+percent',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>'
    ))
    
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Risk Level Distribution', font=dict(size=15, color=COLORS['text']))
    )
    return fig_to_json(fig)

def property_area_chart(data):
    prop_data = data.get('property_data', [])
    
    if not prop_data:
        prop_data = [
            {'property_area': 'Urban', 'predicted_result': 'Approved', 'count': 120},
            {'property_area': 'Urban', 'predicted_result': 'Rejected', 'count': 60},
            {'property_area': 'Semiurban', 'predicted_result': 'Approved', 'count': 140},
            {'property_area': 'Semiurban', 'predicted_result': 'Rejected', 'count': 50},
            {'property_area': 'Rural', 'predicted_result': 'Approved', 'count': 80},
            {'property_area': 'Rural', 'predicted_result': 'Rejected', 'count': 50},
        ]
    
    areas = {}
    for row in prop_data:
        area = row['property_area']
        result = row['predicted_result']
        if area not in areas:
            areas[area] = {'Approved': 0, 'Rejected': 0}
        areas[area][result] = areas[area].get(result, 0) + row['count']
    
    area_names = list(areas.keys())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Approved', x=area_names,
        y=[areas[a].get('Approved', 0) for a in area_names],
        marker_color=COLORS['approved'],
        hovertemplate='<b>%{x}</b><br>Approved: %{y}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        name='Rejected', x=area_names,
        y=[areas[a].get('Rejected', 0) for a in area_names],
        marker_color=COLORS['rejected'],
        hovertemplate='<b>%{x}</b><br>Rejected: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Property Area vs Loan Approval', font=dict(size=15, color=COLORS['text'])),
        barmode='stack',
        xaxis=dict(gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
        yaxis=dict(title='Count', gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
    )
    return fig_to_json(fig)

def monthly_trend_chart(data):
    monthly = data.get('monthly_apps', [])
    
    if not monthly:
        monthly = [
            {'month': '2024-01', 'count': 12}, {'month': '2024-02', 'count': 18},
            {'month': '2024-03', 'count': 22}, {'month': '2024-04', 'count': 15},
            {'month': '2024-05', 'count': 28}, {'month': '2024-06', 'count': 35},
        ]
    
    monthly_sorted = sorted(monthly, key=lambda x: x['month'])
    months = [m['month'] for m in monthly_sorted]
    counts = [m['count'] for m in monthly_sorted]
    
    fig = go.Figure(go.Scatter(
        x=months, y=counts, mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['secondary'], line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(99,102,241,0.15)',
        hovertemplate='Month: %{x}<br>Applications: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Monthly Application Trend', font=dict(size=15, color=COLORS['text'])),
        xaxis=dict(gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
        yaxis=dict(title='Applications', gridcolor=COLORS['grid'], tickfont=dict(color=COLORS['text'])),
    )
    return fig_to_json(fig)

def get_all_charts(analytics_data):
    return {
        'approval_chart': approval_donut_chart(analytics_data),
        'credit_chart': credit_history_chart(analytics_data),
        'loan_amount_chart': loan_amount_histogram(analytics_data),
        'model_chart': model_accuracy_chart(),
        'risk_chart': risk_level_chart(analytics_data),
        'property_chart': property_area_chart(analytics_data),
        'monthly_chart': monthly_trend_chart(analytics_data),
    }
