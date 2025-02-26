from flask import jsonify, request, Blueprint
from models import db, User, TokenBlocklist
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from werkzeug.security import check_password_hash
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)  # FIXED: __name__ instead of name

# Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if email and password are provided
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Query the database for the user
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # Create access token
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "User not found or incorrect password"}), 404


# Login with Google
@auth_bp.route('/login_with_google', methods=['POST'])
def login_with_google():
    data = request.get_json()
    email = data.get('email')

    # Check if email is provided
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Query the database for the user
    user = User.query.filter_by(email=email).first()

    if user:
        # Create access token
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "User not found"}), 404


# Get current user
@auth_bp.route('/current_user', methods=['GET'])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        'id': user.id,
        'first_name': user.first_name,  # FIXED: Corrected key name
        'last_name': user.last_name,
        'email': user.email
    }
    return jsonify(user_data)


# Logout
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({"success": "Logged out successfully"})