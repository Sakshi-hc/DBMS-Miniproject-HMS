import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from hospital_management_system.extensions import db, login_manager
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    # Create Flask application
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "your-super-secret-key-change-this")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configure MySQL database
    mysql_user = os.environ.get("MYSQL_USER", "root")
    mysql_password = os.environ.get("MYSQL_PASSWORD", "Sakshi@12345")
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_port = os.environ.get("MYSQL_PORT", "3306")
    mysql_database = os.environ.get("MYSQL_DATABASE", "hospital_system")

    # Construct MySQL connection string
    database_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
    logger.info(f"Using MySQL database: {mysql_host}:{mysql_port}/{mysql_database}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # Import models here to ensure they're registered with SQLAlchemy
    from hospital_management_system.models import User, Patient, Doctor, Appointment, MedicalRecord, Bill

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Make datetime available to all templates
    from datetime import datetime
    @app.context_processor
    def inject_datetime():
        return {"datetime": datetime}

    # Import and register blueprint
    from hospital_management_system.routes import bp
    app.register_blueprint(bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)