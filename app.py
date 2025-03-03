from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import routes (ensures all endpoints are registered)
from routes import *

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)