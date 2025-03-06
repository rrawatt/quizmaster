from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from models import Subject, Chapter, Quiz, Question, User
from routes import admin_bp
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    subjects = Subject.query.all()
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/dashboard.html', subjects=subjects, users=users)

@admin_bp.route('/subject/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()

        flash('Subject created successfully')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/subject_form.html')

@admin_bp.route('/subject/<int:subject_id>/chapter/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        chapter = Chapter(name=name, description=description, subject=subject)
        db.session.add(chapter)
        db.session.commit()

        flash('Chapter created successfully')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/chapter_form.html', subject=subject)

@admin_bp.route('/chapter/<int:chapter_id>/quiz/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        duration = timedelta(minutes=int(request.form.get('duration')))
        remarks = request.form.get('remarks')

        quiz = Quiz(
            chapter=chapter,
            date_of_quiz=date,
            time_duration=duration,
            remarks=remarks
        )
        db.session.add(quiz)
        db.session.commit()

        flash('Quiz created successfully')
        return redirect(url_for('admin.create_question', quiz_id=quiz.id))

    return render_template('admin/quiz_form.html', chapter=chapter)

@admin_bp.route('/quiz/<int:quiz_id>/question/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        question = Question(
            quiz=quiz,
            question_text=request.form.get('question_text'),
            option_1=request.form.get('option_1'),
            option_2=request.form.get('option_2'),
            option_3=request.form.get('option_3'),
            option_4=request.form.get('option_4'),
            correct_option=int(request.form.get('correct_option'))
        )
        db.session.add(question)
        db.session.commit()

        if 'add_another' in request.form:
            flash('Question added successfully. Add another question.')
            return redirect(url_for('admin.create_question', quiz_id=quiz.id))

        flash('Question added successfully')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/question_form.html', quiz=quiz)