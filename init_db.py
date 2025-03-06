from app import create_app, db
from models import User
from datetime import datetime

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@quizmaster.com').first()
        if not admin:
            admin = User(
                email='admin@quizmaster.com',
                full_name='Quiz Master Admin',
                is_admin=True,
                qualification='Administrator',
                dob=datetime.strptime('2000-01-01', '%Y-%m-%d')
            )
            admin.set_password('admin123')  # Default password
            db.session.add(admin)
            try:
                db.session.commit()
                print("Admin user created successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {e}")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    create_admin()