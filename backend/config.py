import os
from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()
    
class DevelopmentConfig(Config):
    FLASK_DEBUG = True

class ProductionConfig(Config):
    FLASK_DEBUG = False
    FLASK_ENV = 'production'

class Config:
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'client_analysis')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'potensi_model.joblib')
    SCALER_PATH = os.getenv('SCALER_PATH', 'scaler.joblib')
    KMEANS_PATH = os.getenv('KMEANS_PATH', 'kmeans_model.joblib')
    
    # Feature Extraction Configuration
    MIN_SAMPLE_SIZE = int(os.getenv('MIN_SAMPLE_SIZE', 10))
    TRAINING_THRESHOLD = int(os.getenv('TRAINING_THRESHOLD', 50))
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

class DevelopmentConfig(Config):
    FLASK_DEBUG = True

class ProductionConfig(Config):
    FLASK_DEBUG = False
    FLASK_ENV = 'production'
    
    # Production database settings
    DB_HOST = os.getenv('PRODUCTION_DB_HOST', 'localhost')
    DB_USER = os.getenv('PRODUCTION_DB_USER', 'your_production_user')
    DB_PASSWORD = os.getenv('PRODUCTION_DB_PASSWORD', '')
    DB_NAME = os.getenv('PRODUCTION_DB_NAME', 'client_analysis_prod')
    
    # Production model paths
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'potensi_model.joblib')
    SCALER_PATH = os.path.join(os.path.dirname(__file__), 'models', 'scaler.joblib')
    KMEANS_PATH = os.path.join(os.path.dirname(__file__), 'models', 'kmeans_model.joblib')

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()