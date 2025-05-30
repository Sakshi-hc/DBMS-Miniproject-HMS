from app import app, db
from models import User
from datetime import datetime

def create_admin_user():
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return

        # Create new admin user
        admin = User(
            username='admin',
            email='admin@hospital.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            date_created=datetime.utcnow()
        )
        admin.set_password('admin123')  # Set default password

        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user() 