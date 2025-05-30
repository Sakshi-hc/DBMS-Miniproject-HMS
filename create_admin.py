from werkzeug.security import generate_password_hash
import mysql.connector
from datetime import datetime

def create_admin_user():
    # Database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sakshi@12345",
        database="hospital_system"
    )
    cursor = conn.cursor()

    # Generate password hash
    password_hash = generate_password_hash('admin123')

    # SQL query to insert admin user
    sql = """
    INSERT INTO user (username, email, password_hash, first_name, last_name, role, is_active, date_created)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        email = VALUES(email),
        password_hash = VALUES(password_hash),
        first_name = VALUES(first_name),
        last_name = VALUES(last_name),
        role = VALUES(role),
        is_active = VALUES(is_active)
    """
    
    values = (
        'admin',
        'admin@hospital.com',
        password_hash,
        'Admin',
        'User',
        'admin',
        1,
        datetime.utcnow()
    )

    try:
        cursor.execute(sql, values)
        conn.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_admin_user() 