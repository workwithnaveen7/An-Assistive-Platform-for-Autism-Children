from app import create_app, socketio, db
from app.models import User, Child, Content
from flask import redirect, url_for
import os
from app.models import Quiz, QuizQuestion, QuizAttempt

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Child': Child, 'Content': Content}

@app.route('/')
def index():
    """Home page - redirect to login"""
    return redirect(url_for('auth.login'))

def init_sample_data():
    """Initialize sample content for testing"""
    with app.app_context():
        # Clear existing content (optional - remove these lines if you want to keep existing data)
        Content.query.delete()
        db.session.commit()
        
        sample_content = [
            Content(
                title="Calm Breathing Exercise",
                content_type="exercise",
                description="Guided breathing for relaxation",
                suitable_states="alpha,theta,delta",
                difficulty_level=1
            ),
            Content(
                title="Shape Matching Game",
                content_type="game",
                description="Match shapes and colors",
                suitable_states="beta,alpha",
                difficulty_level=2
            ),
            Content(
                title="Story Time Video",
                content_type="video",
                description="Gentle animated story",
                suitable_states="delta,theta,alpha",
                difficulty_level=1
            ),
            Content(
                title="Interactive Puzzle",
                content_type="game",
                description="Colorful puzzle solving",
                suitable_states="beta,gamma",
                difficulty_level=3
            ),
            Content(
                title="Emotion Cards",
                content_type="communication",
                description="Express feelings with cards",
                suitable_states="alpha,beta,theta",
                difficulty_level=1
            ),
            Content(
                title="Music Relaxation",
                content_type="music",  # Changed from 'video' to 'music'
                description="Soothing music and visuals",
                suitable_states="delta,theta,alpha",
                difficulty_level=1
            )
        ]
        
        for content in sample_content:
            db.session.add(content)
        
        db.session.commit()
        print("✓ Sample content initialized")

def init_sample_quizzes():
    """Initialize sample quizzes"""
    with app.app_context():
        if Quiz.query.count() > 0:
            return
        
        # Quiz 1: Colors
        colors_quiz = Quiz(
            title="Learn Colors",
            description="Identify different colors",
            category="colors",
            difficulty_level=1,
            suitable_states="alpha,beta",
            icon="palette"
        )
        db.session.add(colors_quiz)
        db.session.flush()
        
        colors_questions = [
            QuizQuestion(
                quiz_id=colors_quiz.id,
                question_text="What color is the sky on a sunny day?",
                question_type="multiple_choice",
                options='["Blue", "Green", "Red", "Yellow"]',
                correct_answer="Blue",
                order_number=1
            ),
            QuizQuestion(
                quiz_id=colors_quiz.id,
                question_text="What color is fresh grass?",
                question_type="multiple_choice",
                options='["Blue", "Green", "Red", "Yellow"]',
                correct_answer="Green",
                order_number=2
            ),
            QuizQuestion(
                quiz_id=colors_quiz.id,
                question_text="What color is the sun?",
                question_type="multiple_choice",
                options='["Blue", "Green", "Red", "Yellow"]',
                correct_answer="Yellow",
                order_number=3
            ),
            QuizQuestion(
                quiz_id=colors_quiz.id,
                question_text="What color is a ripe apple?",
                question_type="multiple_choice",
                options='["Blue", "Green", "Red", "Yellow"]',
                correct_answer="Red",
                order_number=4
            ),
            QuizQuestion(
                quiz_id=colors_quiz.id,
                question_text="What color is snow?",
                question_type="multiple_choice",
                options='["White", "Black", "Pink", "Purple"]',
                correct_answer="White",
                order_number=5
            )
        ]
        
        for q in colors_questions:
            db.session.add(q)
        
        # Quiz 2: Numbers
        numbers_quiz = Quiz(
            title="Count the Numbers",
            description="Basic counting and math",
            category="math",
            difficulty_level=1,
            suitable_states="beta,gamma",
            icon="calculator"
        )
        db.session.add(numbers_quiz)
        db.session.flush()
        
        numbers_questions = [
            QuizQuestion(
                quiz_id=numbers_quiz.id,
                question_text="What number comes after 5?",
                question_type="multiple_choice",
                options='["4", "6", "7", "8"]',
                correct_answer="6",
                order_number=1
            ),
            QuizQuestion(
                quiz_id=numbers_quiz.id,
                question_text="How many fingers do you have on one hand?",
                question_type="multiple_choice",
                options='["3", "4", "5", "6"]',
                correct_answer="5",
                order_number=2
            ),
            QuizQuestion(
                quiz_id=numbers_quiz.id,
                question_text="What is 2 + 2?",
                question_type="multiple_choice",
                options='["3", "4", "5", "6"]',
                correct_answer="4",
                order_number=3
            ),
            QuizQuestion(
                quiz_id=numbers_quiz.id,
                question_text="What is 5 - 3?",
                question_type="multiple_choice",
                options='["1", "2", "3", "4"]',
                correct_answer="2",
                order_number=4
            ),
            QuizQuestion(
                quiz_id=numbers_quiz.id,
                question_text="How many days are in a week?",
                question_type="multiple_choice",
                options='["5", "6", "7", "8"]',
                correct_answer="7",
                order_number=5
            )
        ]
        
        for q in numbers_questions:
            db.session.add(q)
        
        # Quiz 3: Animals
        animals_quiz = Quiz(
            title="Animal Sounds",
            description="Match animals with their sounds",
            category="animals",
            difficulty_level=1,
            suitable_states="alpha,beta",
            icon="paw"
        )
        db.session.add(animals_quiz)
        db.session.flush()
        
        animals_questions = [
            QuizQuestion(
                quiz_id=animals_quiz.id,
                question_text="What sound does a dog make?",
                question_type="multiple_choice",
                options='["Meow", "Woof", "Moo", "Quack"]',
                correct_answer="Woof",
                order_number=1
            ),
            QuizQuestion(
                quiz_id=animals_quiz.id,
                question_text="What sound does a cat make?",
                question_type="multiple_choice",
                options='["Meow", "Woof", "Moo", "Quack"]',
                correct_answer="Meow",
                order_number=2
            ),
            QuizQuestion(
                quiz_id=animals_quiz.id,
                question_text="What sound does a cow make?",
                question_type="multiple_choice",
                options='["Meow", "Woof", "Moo", "Quack"]',
                correct_answer="Moo",
                order_number=3
            ),
            QuizQuestion(
                quiz_id=animals_quiz.id,
                question_text="What sound does a duck make?",
                question_type="multiple_choice",
                options='["Meow", "Woof", "Moo", "Quack"]',
                correct_answer="Quack",
                order_number=4
            ),
            QuizQuestion(
                quiz_id=animals_quiz.id,
                question_text="What animal says 'Roar'?",
                question_type="multiple_choice",
                options='["Cat", "Dog", "Lion", "Bird"]',
                correct_answer="Lion",
                order_number=5
            )
        ]
        
        for q in animals_questions:
            db.session.add(q)
        
        # Quiz 4: Shapes
        shapes_quiz = Quiz(
            title="Shape Recognition",
            description="Identify different shapes",
            category="shapes",
            difficulty_level=2,
            suitable_states="beta,gamma",
            icon="shapes"
        )
        db.session.add(shapes_quiz)
        db.session.flush()
        
        shapes_questions = [
            QuizQuestion(
                quiz_id=shapes_quiz.id,
                question_text="How many sides does a triangle have?",
                question_type="multiple_choice",
                options='["2", "3", "4", "5"]',
                correct_answer="3",
                order_number=1
            ),
            QuizQuestion(
                quiz_id=shapes_quiz.id,
                question_text="How many sides does a square have?",
                question_type="multiple_choice",
                options='["2", "3", "4", "5"]',
                correct_answer="4",
                order_number=2
            ),
            QuizQuestion(
                quiz_id=shapes_quiz.id,
                question_text="A circle has corners. True or False?",
                question_type="true_false",
                options='["True", "False"]',
                correct_answer="False",
                order_number=3
            ),
            QuizQuestion(
                quiz_id=shapes_quiz.id,
                question_text="What shape is a ball?",
                question_type="multiple_choice",
                options='["Square", "Triangle", "Circle", "Rectangle"]',
                correct_answer="Circle",
                order_number=4
            ),
            QuizQuestion(
                quiz_id=shapes_quiz.id,
                question_text="What shape is a book?",
                question_type="multiple_choice",
                options='["Circle", "Triangle", "Square", "Rectangle"]',
                correct_answer="Rectangle",
                order_number=5
            )
        ]
        
        for q in shapes_questions:
            db.session.add(q)
        
        # Quiz 5: Emotions
        emotions_quiz = Quiz(
            title="Understanding Emotions",
            description="Learn about different feelings",
            category="emotions",
            difficulty_level=1,
            suitable_states="alpha,theta",
            icon="smile"
        )
        db.session.add(emotions_quiz)
        db.session.flush()
        
        emotions_questions = [
            QuizQuestion(
                quiz_id=emotions_quiz.id,
                question_text="When someone smiles, they are usually...",
                question_type="multiple_choice",
                options='["Happy", "Sad", "Angry", "Scared"]',
                correct_answer="Happy",
                order_number=1
            ),
            QuizQuestion(
                quiz_id=emotions_quiz.id,
                question_text="When someone cries, they might be...",
                question_type="multiple_choice",
                options='["Happy", "Sad", "Excited", "Proud"]',
                correct_answer="Sad",
                order_number=2
            ),
            QuizQuestion(
                quiz_id=emotions_quiz.id,
                question_text="It's okay to feel sad sometimes. True or False?",
                question_type="true_false",
                options='["True", "False"]',
                correct_answer="True",
                order_number=3
            ),
            QuizQuestion(
                quiz_id=emotions_quiz.id,
                question_text="What should you do when you feel angry?",
                question_type="multiple_choice",
                options='["Hit someone", "Take deep breaths", "Run away", "Cry loudly"]',
                correct_answer="Take deep breaths",
                order_number=4
            ),
            QuizQuestion(
                quiz_id=emotions_quiz.id,
                question_text="When a friend is sad, you should...",
                question_type="multiple_choice",
                options='["Ignore them", "Laugh at them", "Be kind to them", "Walk away"]',
                correct_answer="Be kind to them",
                order_number=5
            )
        ]
        
        for q in emotions_questions:
            db.session.add(q)
        
        db.session.commit()
        print("✓ Sample quizzes initialized (5 quizzes, 25 questions)")


# Update the main section
if __name__ == '__main__':
    init_sample_data()
    init_sample_quizzes()  # Add this line
    print(" * Starting Autism Assistive Platform")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)


# if __name__ == '__main__':
#     init_sample_data()
#     print(" * Starting Autism Assistive Platform")
#     print(" * EEG-enabled adaptive learning system")
#     socketio.run(app, debug=True, host='0.0.0.0', port=5000)
