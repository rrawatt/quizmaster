from app import create_app, db
from models import Subject, Chapter, Quiz, Question
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        # Create Subjects
        math = Subject(name='Mathematics', description='Basic to advanced mathematics concepts')
        science = Subject(name='Science', description='General science topics')
        
        db.session.add_all([math, science])
        db.session.commit()
        
        # Create Chapters
        algebra = Chapter(name='Algebra', description='Basic algebraic concepts', subject=math)
        geometry = Chapter(name='Geometry', description='Basic geometric principles', subject=math)
        physics = Chapter(name='Physics', description='Basic physics concepts', subject=science)
        chemistry = Chapter(name='Chemistry', description='Introduction to chemistry', subject=science)
        
        db.session.add_all([algebra, geometry, physics, chemistry])
        db.session.commit()
        
        # Create Quizzes
        quiz1 = Quiz(
            chapter=algebra,
            date_of_quiz=datetime.now(),
            time_duration=timedelta(minutes=10),
            remarks='Basic algebra quiz'
        )
        
        quiz2 = Quiz(
            chapter=physics,
            date_of_quiz=datetime.now(),
            time_duration=timedelta(minutes=15),
            remarks='Basic physics quiz'
        )
        
        db.session.add_all([quiz1, quiz2])
        db.session.commit()
        
        # Create Questions for Algebra Quiz
        algebra_questions = [
            {
                'text': 'What is the value of x in 2x + 4 = 10?',
                'options': ['2', '3', '4', '5'],
                'correct': 2
            },
            {
                'text': 'Simplify: 3(x + 2) - 2x',
                'options': ['x + 6', '5x + 6', 'x + 2', '3x + 6'],
                'correct': 1
            },
            {
                'text': 'Solve for y: y/3 = 6',
                'options': ['2', '18', '12', '9'],
                'correct': 2
            }
        ]
        
        # Create Questions for Physics Quiz
        physics_questions = [
            {
                'text': 'What is the SI unit of force?',
                'options': ['Newton', 'Joule', 'Watt', 'Pascal'],
                'correct': 1
            },
            {
                'text': 'Which of these is a vector quantity?',
                'options': ['Mass', 'Temperature', 'Velocity', 'Time'],
                'correct': 3
            },
            {
                'text': 'What is the formula for work done?',
                'options': ['W = mg', 'W = F × d', 'W = mv', 'W = ma'],
                'correct': 2
            }
        ]
        
        # Add Algebra Questions
        for q in algebra_questions:
            question = Question(
                quiz=quiz1,
                question_text=q['text'],
                option_1=q['options'][0],
                option_2=q['options'][1],
                option_3=q['options'][2],
                option_4=q['options'][3],
                correct_option=q['correct']
            )
            db.session.add(question)
        
        # Add Physics Questions
        for q in physics_questions:
            question = Question(
                quiz=quiz2,
                question_text=q['text'],
                option_1=q['options'][0],
                option_2=q['options'][1],
                option_3=q['options'][2],
                option_4=q['options'][3],
                correct_option=q['correct']
            )
            db.session.add(question)
        
        db.session.commit()
        print("Sample data has been created successfully!")

if __name__ == '__main__':
    seed_database()
