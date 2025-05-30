from app import app, db
from datetime import datetime, date
from sqlalchemy import text

def update_schema():
    with app.app_context():
        try:
            # Convert date_registered from DATETIME to DATE
            db.session.execute(text("""
                ALTER TABLE patient 
                MODIFY COLUMN date_registered DATE DEFAULT (CURRENT_DATE);
            """))
            
            # Update existing records to use only the date part
            db.session.execute(text("""
                UPDATE patient 
                SET date_registered = DATE(date_registered);
            """))
            
            db.session.commit()
            print("Schema updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema() 