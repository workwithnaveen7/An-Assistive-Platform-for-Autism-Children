from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='parent')  # parent or child
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    children = db.relationship('Child', backref='parent', lazy=True, foreign_keys='Child.parent_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Child(db.Model):
    __tablename__ = 'children'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eeg_enabled = db.Column(db.Boolean, default=False)
    current_state = db.Column(db.String(20), default='alpha')  # delta, theta, alpha, beta, gamma
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    brain_states = db.relationship('BrainState', backref='child', lazy=True, cascade='all, delete-orphan')
    routines = db.relationship('Routine', backref='child', lazy=True, cascade='all, delete-orphan')
    mood_logs = db.relationship('MoodLog', backref='child', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', backref='child', lazy=True, cascade='all, delete-orphan')

class BrainState(db.Model):
    __tablename__ = 'brain_states'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    state = db.Column(db.String(20), nullable=False)  # delta, theta, alpha, beta, gamma
    frequency = db.Column(db.Float)  # Hz
    source = db.Column(db.String(20), nullable=False)  # 'eeg' or 'manual'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BrainState {self.state} at {self.frequency}Hz>'

class Routine(db.Model):
    __tablename__ = 'routines'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time_slot = db.Column(db.String(50))  # morning, afternoon, evening
    icon = db.Column(db.String(100))  # icon name or path
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MoodLog(db.Model):
    __tablename__ = 'mood_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    mood = db.Column(db.String(50), nullable=False)  # happy, sad, anxious, calm
    intensity = db.Column(db.Integer)  # 1-5 scale
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)  # game, learning, communication
    duration_seconds = db.Column(db.Integer)
    completion_rate = db.Column(db.Float)  # 0-100
    brain_state = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Content(db.Model):
    __tablename__ = 'content'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # game, video, exercise, communication
    description = db.Column(db.Text)
    suitable_states = db.Column(db.String(200))  # comma-separated: delta,theta,alpha
    difficulty_level = db.Column(db.Integer, default=1)  # 1-5
    content_url = db.Column(db.String(500))
    thumbnail = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Add these new models at the end of the file

class Quiz(db.Model):
    """Quiz model for learning modules"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # math, language, colors, shapes, animals, etc.
    difficulty_level = db.Column(db.Integer, default=1)  # 1=easy, 2=medium, 3=hard
    suitable_states = db.Column(db.String(200))  # alpha,beta,gamma
    icon = db.Column(db.String(50), default='book')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')

class QuizQuestion(db.Model):
    """Individual questions in a quiz"""
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='multiple_choice')  # multiple_choice, true_false, image_choice
    options = db.Column(db.JSON)  # List of options
    correct_answer = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.Text)  # Optional explanation for answer
    order_number = db.Column(db.Integer, default=0)

class QuizAttempt(db.Model):
    """Track quiz attempts by children"""
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, default=0)  # Number of correct answers
    total_questions = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    time_taken_seconds = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.JSON)  # Store user's answers
