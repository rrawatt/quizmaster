from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import db, login_manager
from models import User
from routes import auth_bp
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))

        flash('Invalid email or password')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d')

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))

        user = User(
            email=email,
            full_name=full_name,
            qualification=qualification,
            dob=dob
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))