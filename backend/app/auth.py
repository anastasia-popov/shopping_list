from flask import request, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user
from app import db, oauth
from app.models import User
import os



# OAuth providers
providers = {
    'google': {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'access_token_url': 'https://oauth2.googleapis.com/token',
        'scope': 'openid email profile'
    },
    'github': {
        'client_id': os.getenv('GITHUB_CLIENT_ID'),
        'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'scope': 'user:email'
    },
    'facebook': {
        'client_id': os.getenv('FACEBOOK_CLIENT_ID'),
        'client_secret': os.getenv('FACEBOOK_CLIENT_SECRET'),
        'authorize_url': 'https://www.facebook.com/v12.0/dialog/oauth',
        'access_token_url': 'https://graph.facebook.com/v12.0/oauth/access_token',
        'scope': 'email'
    }
}

for name, provider in providers.items():
    oauth.register(
        name=name,
        client_id=provider['client_id'],
        client_secret=provider['client_secret'],
        authorize_url=provider['authorize_url'],
        access_token_url=provider['access_token_url'],
        client_kwargs={'scope': provider['scope']}
    )
