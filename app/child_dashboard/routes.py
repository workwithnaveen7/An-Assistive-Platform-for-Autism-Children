from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from app import db, socketio
from app.child_dashboard import child_bp
from app.models import Child, BrainState, Content, Routine, MoodLog, ActivityLog
from app.eeg_processor.classifier import EEGClassifier
from datetime import datetime
from flask_socketio import emit
from config import Config
from app.models import Quiz, QuizQuestion, QuizAttempt

eeg_classifier = EEGClassifier()

@child_bp.route('/dashboard/<int:child_id>')
@login_required
def dashboard(child_id):
    child = Child.query.get_or_404(child_id)
    
    # Verify parent has access
    if child.parent_id != current_user.id:
        return "Unauthorized", 403
    
    # Get current brain state
    latest_state = BrainState.query.filter_by(child_id=child_id)\
        .order_by(BrainState.timestamp.desc()).first()
    
    current_state = latest_state.state if latest_state else 'alpha'
    
    # Get suitable content for current state
    content = Content.query.filter(
        Content.suitable_states.contains(current_state)
    ).limit(6).all()
    
    # Get today's routines
    routines = Routine.query.filter_by(child_id=child_id).all()
    
    return render_template('child/dashboard.html', 
                         child=child,
                         current_state=current_state,
                         content=content,
                         routines=routines,
                         brain_states=Config.BRAIN_STATES)

@child_bp.route('/api/eeg-input', methods=['POST'])
@login_required
def receive_eeg_data():
    """
    Endpoint to receive real-time EEG data from hardware device
    Expected JSON: {
        'child_id': int,
        'frequency': float OR 'raw_signal': [float, float, ...]
    }
    """
    data = request.json
    child_id = data.get('child_id')
    
    child = Child.query.get_or_404(child_id)
    
    if child.parent_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Process EEG data
    if 'raw_signal' in data:
        # Process raw signal
        result = eeg_classifier.process_eeg_signal(data['raw_signal'])
        frequency = result['dominant_frequency']
        brain_state = result['brain_state']
    else:
        # Direct frequency input
        frequency = data.get('frequency')
        brain_state = eeg_classifier.classify_frequency(frequency)
    
    # Save to database
    brain_state_record = BrainState(
        child_id=child_id,
        state=brain_state,
        frequency=frequency,
        source='eeg'
    )
    db.session.add(brain_state_record)
    
    # Update child's current state
    child.current_state = brain_state
    db.session.commit()
    
    # Emit real-time update to connected clients
    socketio.emit('brain_state_update', {
        'child_id': child_id,
        'brain_state': brain_state,
        'frequency': frequency,
        'timestamp': brain_state_record.timestamp.isoformat(),
        'state_info': eeg_classifier.get_state_info(brain_state)
    }, room=f'child_{child_id}')
    
    return jsonify({
        'success': True,
        'brain_state': brain_state,
        'frequency': frequency
    })

@child_bp.route('/api/manual-input', methods=['POST'])
@login_required
def manual_state_input():
    """
    Endpoint for parent to manually set child's state
    Expected JSON: {
        'child_id': int,
        'state': str (delta, theta, alpha, beta, gamma)
    }
    """
    data = request.json
    child_id = data.get('child_id')
    state = data.get('state')
    
    child = Child.query.get_or_404(child_id)
    
    if child.parent_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate state
    if state not in Config.BRAIN_STATES:
        return jsonify({'error': 'Invalid state'}), 400
    
    # Save to database
    brain_state_record = BrainState(
        child_id=child_id,
        state=state,
        source='manual'
    )
    db.session.add(brain_state_record)
    
    # Update child's current state
    child.current_state = state
    db.session.commit()
    
    # Emit real-time update
    socketio.emit('brain_state_update', {
        'child_id': child_id,
        'brain_state': state,
        'source': 'manual',
        'timestamp': brain_state_record.timestamp.isoformat(),
        'state_info': eeg_classifier.get_state_info(state)
    }, room=f'child_{child_id}')
    
    return jsonify({
        'success': True,
        'brain_state': state
    })

@child_bp.route('/api/content/<string:brain_state>')
@login_required
def get_content_for_state(brain_state):
    """Get content suitable for specific brain state"""
    content = Content.query.filter(
        Content.suitable_states.contains(brain_state)
    ).all()
    
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'type': c.content_type,
        'description': c.description,
        'url': c.content_url,
        'thumbnail': c.thumbnail
    } for c in content])

@child_bp.route('/api/mood-log', methods=['POST'])
@login_required
def log_mood():
    """Log child's mood"""
    data = request.json
    
    mood_log = MoodLog(
        child_id=data['child_id'],
        mood=data['mood'],
        intensity=data.get('intensity', 3),
        notes=data.get('notes', '')
    )
    db.session.add(mood_log)
    db.session.commit()
    
    return jsonify({'success': True, 'id': mood_log.id})

@child_bp.route('/api/activity-log', methods=['POST'])
@login_required
def log_activity():
    """Log activity completion"""
    data = request.json
    
    activity_log = ActivityLog(
        child_id=data['child_id'],
        activity_type=data['activity_type'],
        duration_seconds=data.get('duration_seconds', 0),
        completion_rate=data.get('completion_rate', 100),
        brain_state=data.get('brain_state')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return jsonify({'success': True, 'id': activity_log.id})

# SocketIO event handlers
@socketio.on('join_child_room')
def handle_join_child_room(data):
    """Join a room for real-time updates for specific child"""
    child_id = data.get('child_id')
    room = f'child_{child_id}'
    from flask_socketio import join_room
    join_room(room)
    emit('joined_room', {'child_id': child_id, 'room': room})

@child_bp.route('/activity/<int:child_id>/<string:activity_type>')
@login_required
def activity(child_id, activity_type):
    """Launch specific activity"""
    child = Child.query.get_or_404(child_id)
    
    if child.parent_id != current_user.id:
        return "Unauthorized", 403
    
    # Map activity types to templates
    activity_templates = {
        'exercise': 'activities/breathing.html',
        'breathing': 'activities/breathing.html',
        'game': 'activities/puzzle.html',
        'puzzle': 'activities/puzzle.html',
        'shape': 'activities/puzzle.html',
        'video': 'activities/story_video.html',
        'story': 'activities/story_video.html',
        'communication': 'activities/communication.html',
        'emotion': 'activities/communication.html',
        'music': 'activities/music.html',
        'sensory': 'activities/music.html'
    }
    
    template = activity_templates.get(activity_type.lower(), 'activities/breathing.html')
    
    return render_template(template, child_id=child_id, activity_id=0)

# Add this route
@child_bp.route('/api/quizzes/<string:state>')
@login_required
def get_quizzes(state):
    """Get quizzes suitable for current brain state"""
    quizzes = Quiz.query.filter(
        (Quiz.suitable_states.like(f'%{state}%')) | 
        (Quiz.suitable_states == None)
    ).all()
    
    return jsonify([{
        'id': q.id,
        'title': q.title,
        'description': q.description,
        'category': q.category,
        'difficulty_level': q.difficulty_level,
        'icon': q.icon,
        'question_count': len(q.questions)
    } for q in quizzes])

@child_bp.route('/quiz/<int:child_id>/<int:quiz_id>')
@login_required
def take_quiz(child_id, quiz_id):
    """Take a quiz"""
    child = Child.query.get_or_404(child_id)
    
    if child.parent_id != current_user.id:
        return "Unauthorized", 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Convert quiz questions to dictionaries for JSON serialization
    questions_data = []
    for question in quiz.questions:
        questions_data.append({
            'id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'options': question.options,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'order_number': question.order_number
        })
    
    # Sort by order number
    questions_data.sort(key=lambda x: x['order_number'])
    
    return render_template('quiz/take_quiz.html', 
                         child_id=child_id, 
                         quiz=quiz,
                         questions_json=questions_data)


@child_bp.route('/api/quiz-attempt', methods=['POST'])
@login_required
def save_quiz_attempt():
    """Save quiz attempt"""
    data = request.json
    
    attempt = QuizAttempt(
        child_id=data['child_id'],
        quiz_id=data['quiz_id'],
        score=data['score'],
        total_questions=data['total_questions'],
        percentage=data['percentage'],
        time_taken_seconds=data['time_taken_seconds'],
        answers=data['answers']
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    return jsonify({'success': True})