import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'testing54321'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'autism_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # SocketIO configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # EEG Configuration
    EEG_SAMPLING_RATE = 256  # Hz
    EEG_UPDATE_INTERVAL = 1  # seconds
    
    # Brain State Thresholds
    BRAIN_STATES = {
        'delta': {'range': (0, 4), 'label': 'Sleep/Deep Rest', 'color': '#9C27B0'},
        'theta': {'range': (4, 8), 'label': 'Tired/Drowsy', 'color': '#3F51B5'},
        'alpha': {'range': (8, 12), 'label': 'Calm/Relaxed', 'color': '#4CAF50'},
        'beta': {'range': (13, 30), 'label': 'Alert/Active', 'color': '#FF9800'},
        'gamma': {'range': (30, 100), 'label': 'Highly Engaged', 'color': '#F44336'}
    }
