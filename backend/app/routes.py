from flask import request, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, oauth
from app.models import User

@app.route('/auth-status', methods=['GET'])
def auth_status():
    print(current_user)
    return {'authenticated': current_user.is_authenticated}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'email': u.email} for u in users])

@app.route('/login/<provider>')
def oauth_login(provider):
    if provider not in providers:
        return 'Provider not supported', 400
    return oauth.create_client(provider).authorize_redirect(url_for('authorize', provider=provider, _external=True))

@app.route('/authorize/<provider>')
def authorize(provider):
    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    user_info = client.parse_id_token(token) if provider == 'google' else client.get('user').json()
    
    email = user_info.get('email', user_info.get('login', '') + '@github.com')
    username = user_info.get('name', user_info.get('login', 'Unknown'))
    user = User.query.filter_by(email=email).first()
    
    if not user:
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('get_users'))

