from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User

user_bp = Blueprint('user_bp', name)

# Add a user (admin/technician/guard)
@user_bp.route("/user", methods=["POST"])
def add_user():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data['email']
    password = generate_password_hash(data['password'])
    role = data.get('role', 'user')  # Default role is 'user'

if User.query.filter_by(email=email).first():
    return jsonify({'msg': 'User already exists'}), 400

new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, role=role)
db.session.add(new_user)
db.session.commit()
return jsonify({'msg': 'User created successfully'}), 201
Fetch all users
@user_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
    return jsonify(output), 200

# Fetch a single user by ID
@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }), 200
    else:
        return jsonify({'msg': 'User not found'}), 404

# Update a user
@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)

if user:
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({'msg': 'User updated successfully'}), 200
else:
    return jsonify({'msg': 'User not found'}), 404
# Delete a user
@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'msg': 'User deleted successfully'}), 200
    else:
        return jsonify({'msg': 'User not found'}), 404
