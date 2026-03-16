import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'loan-approval-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'loan_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.path.join(BASE_DIR, 'trained_models', 'best_model.pkl')
    PIPELINE_PATH = os.path.join(BASE_DIR, 'trained_models', 'pipeline.pkl')
    DATASET_PATH = os.path.join(BASE_DIR, 'data', 'loan_data.csv')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
