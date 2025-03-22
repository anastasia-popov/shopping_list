from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS


import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/cooking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')


app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # For cross-origin requests
app.config['SESSION_COOKIE_SECURE'] = True      # Required when SAMESITE=None (must use HTTPS)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CORS(app, supports_credentials=True, origins=[os.getenv('FRONTEND_BASE_URL')])


from app import models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


oauth = OAuth(app)

# Import routes after initializing app
from app import routes
