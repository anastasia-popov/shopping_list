from flask import request, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, oauth
from app.models import User, Product, Department, ShoppingList

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
 
# Shopping List Endpoints
@app.route('/shopping-list/add-product', methods=['POST'])
@login_required
def add_product_to_list():
    data = request.json
    product_name = data.get('product_name')
    if not product_name:
        return jsonify({'error': 'Missing product_name'}), 400

    normalized_name = product_name.strip().lower()

    shopping_list = current_user.shopping_list
    if not shopping_list:
        shopping_list = ShoppingList(user_id=current_user.id)
        db.session.add(shopping_list)
        db.session.commit()

    product = Product.query.filter(db.func.lower(Product.name) == normalized_name).first()

    if not product:
        missing_department = Department.query.filter_by(name="other").first()
        if not missing_department:
            missing_department = Department(name="other")
            db.session.add(missing_department)
            db.session.commit()

        product = Product(name=normalized_name, department_id=missing_department.id)
        db.session.add(product)
        db.session.commit()

    if product not in shopping_list.products:
        shopping_list.products.append(product)
        db.session.commit()

    return jsonify({'message': f"Product '{product.name}' added to shopping list"})

@app.route('/shopping-list/remove-product', methods=['POST'])
@login_required
def remove_product_from_list():
    data = request.json
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Missing product_id'}), 400

    shopping_list = current_user.shopping_list
    if not shopping_list:
        return jsonify({'error': 'No shopping list found'}), 404

    product = Product.query.get_or_404(product_id)
    if product in shopping_list.products:
        shopping_list.products.remove(product)
        db.session.commit()
    return jsonify({'message': 'Product removed from shopping list'})

@app.route('/shopping-list', methods=['GET'])
@login_required
def get_user_shopping_list():
    shopping_list = current_user.shopping_list
    if not shopping_list:
        return jsonify({'message': 'No shopping list found'}), 404
    products = [{
        'id': p.id,
        'name': p.name,
        'department': p.department.name if p.department else None
    } for p in shopping_list.products]
    return jsonify({'id': shopping_list.id, 'products': products})


