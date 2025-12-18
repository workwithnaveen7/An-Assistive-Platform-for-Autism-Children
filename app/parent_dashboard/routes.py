
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.parent_dashboard import parent_bp
from app.models import Child, BrainState, Routine, MoodLog, ActivityLog
from datetime import datetime, timedelta
from sqlalchemy import func
from config import Config
from app.models import Quiz, QuizQuestion, QuizAttempt

@parent_bp.route('/dashboard')
@login_required
def dashboard():
    """Parent dashboard showing all children and overview"""
    children = Child.query.filter_by(parent_id=current_user.id).all()
    
    # Get statistics for each child
    child_stats = []
    for child in children:
        # Get today's activity count
        today = datetime.utcnow().date()
        activity_count = ActivityLog.query.filter(
            ActivityLog.child_id == child.id,
            func.date(ActivityLog.timestamp) == today
        ).count()
        
        # Get latest mood
        latest_mood = MoodLog.query.filter_by(child_id=child.id)\
            .order_by(MoodLog.timestamp.desc()).first()
        
        child_stats.append({
            'child': child,
            'activity_count': activity_count,
            'latest_mood': latest_mood.mood if latest_mood else 'N/A'
        })
    
    return render_template('parent/dashboard.html', 
                         child_stats=child_stats,
                         brain_states=Config.BRAIN_STATES)


@parent_bp.route('/child/add', methods=['POST'])
@login_required
def add_child():
    """Add a new child profile"""
    data = request.json
    
    child = Child(
        name=data['name'],
        age=data.get('age'),
        parent_id=current_user.id,
        eeg_enabled=data.get('eeg_enabled', False)
    )
    db.session.add(child)
    db.session.commit()
    
    return jsonify({'success': True, 'child_id': child.id})

@parent_bp.route('/child/<int:child_id>/settings', methods=['GET', 'POST'])
@login_required
def child_settings(child_id):
    """Manage child settings"""
    child = Child.query.get_or_404(child_id)
    
    if child.parent_id != current_user.id:
        return "Unauthorized", 403
    
    if request.method == 'POST':
        data = request.json
        child.name = data.get('name', child.name)
        child.age = data.get('age', child.age)
        child.eeg_enabled = data.get('eeg_enabled', child.eeg_enabled)
        db.session.commit()
        
        return jsonify({'success': True})
    
    return render_template('parent/child_settings.html', child=child)

@parent_bp.route('/child/<int:child_id>/routines', methods=['GET', 'POST'])
@login_required
def manage_routines(child_id):
    """Manage child's routines"""
    child = Child.query.get_or_404(child_id)
    
    if child.parent_id != current_user.id:
        return "Unauthorized", 403
    
    if request.method == 'POST':
        data = request.json
        
        routine = Routine(
            child_id=child_id,
            title=data['title'],
            description=data.get('description', ''),
            time_slot=data.get('time_slot', 'morning'),
            icon=data.get('icon', 'calendar')
        )
        db.session.add(routine)
        db.session.commit()
        
        return jsonify({'success': True, 'routine_id': routine.id})
    
    routines = Routine.query.filter_by(child_id=child_id).all()
    return render_template('parent/routines.html', child=child, routines=routines)

@parent_bp.route('/child/<int:child_id>/analytics')
@login_required
def analytics(child_id):
    """View behavioral analytics for child"""
    child = Child.query.get_or_404(child_id)
    
    if child.parent_id != current_user.id:
        return "Unauthorized", 403
    
    # Get brain state distribution (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    brain_states_data = db.session.query(
        BrainState.state,
        func.count(BrainState.id).label('count')
    ).filter(
        BrainState.child_id == child_id,
        BrainState.timestamp >= week_ago
    ).group_by(BrainState.state).all()
    
    state_distribution = {state: count for state, count in brain_states_data}
    
    # Get mood trends
    moods = MoodLog.query.filter(
        MoodLog.child_id == child_id,
        MoodLog.timestamp >= week_ago
    ).order_by(MoodLog.timestamp).all()
    
    mood_data = [{
        'timestamp': m.timestamp.isoformat(),
        'mood': m.mood,
        'intensity': m.intensity
    } for m in moods]
    
    # Get activity statistics
    activities = db.session.query(
        ActivityLog.activity_type,
        func.count(ActivityLog.id).label('count'),
        func.avg(ActivityLog.completion_rate).label('avg_completion')
    ).filter(
        ActivityLog.child_id == child_id,
        ActivityLog.timestamp >= week_ago
    ).group_by(ActivityLog.activity_type).all()
    
    activity_stats = [{
        'type': act_type,
        'count': count,
        'avg_completion': round(avg_comp, 1) if avg_comp else 0
    } for act_type, count, avg_comp in activities]

    # NEW: Quiz statistics
    quiz_stats = db.session.query(
        Quiz.title,
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(QuizAttempt.percentage).label('avg_score'),
        func.max(QuizAttempt.percentage).label('best_score')
    ).join(QuizAttempt).filter(
        QuizAttempt.child_id == child_id
    ).group_by(Quiz.title).all()

    return render_template('parent/analytics.html',
                         child=child,
                         state_distribution=state_distribution,
                         mood_data=mood_data,
                         activity_stats=activity_stats,
                         brain_states=Config.BRAIN_STATES,
                         quiz_stats=quiz_stats)
