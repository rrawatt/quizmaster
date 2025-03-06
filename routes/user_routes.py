from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app import db
from models import Subject, Quiz, Question, Score
from routes import user_bp
from datetime import datetime, timedelta

@user_bp.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.query.all()
    user_scores = Score.query.filter_by(user_id=current_user.id).all()
    return render_template('user/dashboard.html', subjects=subjects, scores=user_scores)

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

    return render_template('user/quiz_list.html', quizzes=quizzes)

@user_bp.route('/quiz/<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Check if user has already attempted this quiz
    existing_score = Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first()
    if existing_score:
        flash('You have already attempted this quiz.')
        return redirect(url_for('user.dashboard'))

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