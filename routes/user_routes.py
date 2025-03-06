from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app import db
from models import Subject, Quiz, Question, Score
from routes import user_bp
from datetime import datetime, timedelta
from sqlalchemy import func

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get all subjects
    subjects = Subject.query.all()

    # Get user's scores
    user_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).all()

    # Calculate overall statistics
    total_quizzes_taken = len(user_scores)
    average_score = sum(score.score for score in user_scores) / total_quizzes_taken if total_quizzes_taken > 0 else 0

    # Calculate completion rate
    total_quizzes = Quiz.query.count()
    completion_rate = (total_quizzes_taken / total_quizzes * 100) if total_quizzes > 0 else 0

    # Get recent scores
    recent_scores = user_scores[:5]  # Last 5 quiz attempts

    # Prepare performance trend data
    performance_dates = []
    performance_scores = []
    for score in reversed(user_scores[-10:]):  # Last 10 attempts
        performance_dates.append(score.timestamp.strftime('%Y-%m-%d'))
        performance_scores.append(score.score)

    # Calculate subject-wise performance
    subject_performance = {}
    for score in user_scores:
        subject_name = score.quiz.chapter.subject.name
        if subject_name not in subject_performance:
            subject_performance[subject_name] = {'total': 0, 'count': 0}
        subject_performance[subject_name]['total'] += score.score
        subject_performance[subject_name]['count'] += 1

    subject_names = []
    subject_scores = []
    for subject_name, data in subject_performance.items():
        subject_names.append(subject_name)
        subject_scores.append(data['total'] / data['count'])

    return render_template('user/dashboard.html',
                         subjects=subjects,
                         recent_scores=recent_scores,
                         average_score=average_score,
                         total_quizzes_taken=total_quizzes_taken,
                         completion_rate=round(completion_rate, 1),
                         performance_dates=performance_dates,
                         performance_scores=performance_scores,
                         subject_names=subject_names,
                         subject_scores=subject_scores)

@user_bp.route('/quizzes')
@login_required
def quiz_list():
    subject_id = request.args.get('subject_id', type=int)
    chapter_id = request.args.get('chapter_id', type=int)

    if subject_id:
        subject = Subject.query.get_or_404(subject_id)
        quizzes = Quiz.query.join(Quiz.chapter).filter_by(subject_id=subject_id).all()
    elif chapter_id:
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    else:
        quizzes = Quiz.query.all()

    # Get user's best scores for each quiz
    completed_quizzes = {}
    for score in Score.query.filter_by(user_id=current_user.id).all():
        if score.quiz_id not in completed_quizzes or score.score > completed_quizzes[score.quiz_id].score:
            completed_quizzes[score.quiz_id] = score

    return render_template('user/quiz_list.html', quizzes=quizzes, completed_quizzes=completed_quizzes)

@user_bp.route('/quiz/<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        score = 0
        total_questions = len(quiz.questions)

        # Verify quiz time hasn't expired
        current_time = datetime.utcnow()
        if 'quiz_start_time' in request.cookies:
            start_time = datetime.fromtimestamp(float(request.cookies['quiz_start_time']))
            elapsed_time = current_time - start_time
            if elapsed_time > quiz.time_duration:
                flash('Quiz time has expired. Your answers have been submitted automatically.')

        for question in quiz.questions:
            selected_option = int(request.form.get(f'question_{question.id}', 0))
            if selected_option == question.correct_option:
                score += 1

        final_score = (score / total_questions) * 100 if total_questions > 0 else 0

        quiz_score = Score(
            quiz=quiz,
            user=current_user,
            score=final_score,
            timestamp=datetime.utcnow()
        )
        db.session.add(quiz_score)
        db.session.commit()

        return redirect(url_for('user.quiz_results', score_id=quiz_score.id))

    # Set quiz start time in cookie
    response = make_response(render_template('user/take_quiz.html', quiz=quiz))
    response.set_cookie('quiz_start_time', str(datetime.utcnow().timestamp()))
    return response

@user_bp.route('/quiz/results/<int:score_id>')
@login_required
def quiz_results(score_id):
    score = Score.query.get_or_404(score_id)
    if score.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('user.dashboard'))

    return render_template('user/quiz_results.html', score=score)