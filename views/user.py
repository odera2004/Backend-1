import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from models import db, User

user_bp = Blueprint('user_bp', __name__)

UPLOAD_FOLDER = 'static/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Add a user (admin/technician/guard)
@user_bp.route("/user", methods=["POST"])
def add_user():
    data = request.form
    file = request.files.get('profile_picture')

    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data['email']
    password = generate_password_hash(data['password'])
    role = data.get('role', 'user')

    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'User already exists'}), 400
    
    profile_picture = "default.jpg"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        profile_picture = filename

    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, role=role, profile_picture=profile_picture)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully"}), 201

# Fetch all users
@user_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'profile_picture': user.profile_picture
        })
    return jsonify(output), 200

# Fetch a single user by ID
@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'profile_picture': user.profile_picture
        }), 200
    return jsonify({"msg": "User not found"}), 404

# Update a user (excluding profile picture)
@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)

    if user:
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password)
        user.is_admin = data.get('is_admin', user.is_admin)
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
        return jsonify({"msg": "User deleted successfully"}), 200
    
    return jsonify({"msg": "User not found"}), 404
