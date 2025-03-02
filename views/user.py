from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User,Technician,Guard

user_bp = Blueprint('user_bp', __name__)

# Add a user 
@user_bp.route("/user", methods=["POST"])
def add_user():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data['email']
    password = generate_password_hash(data['password'])
    role = data.get('role', 'user') 

    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'User already exists'}), 400
    
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'User created successfully'}), 201

# Fetch all users
@user_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'id': user.id,
            'first name': user.first_name,
            'last name': user.last_name,
            'email': user.email,
        })
    return jsonify(output), 200

#Fetch User by Email
@user_bp.route("/users/email/<string:email>", methods=["GET"])
def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'msg': 'User does not exist'}), 404
    
    return jsonify({
        'id': user.id,
    }), 200


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
    

#Change Role of user
@user_bp.route("/promote_user", methods=["POST"])
def promote_user():
    data = request.get_json()
    email = data.get("email")
    role = data.get("role")

    # Validate input
    if not email:
        return jsonify({"msg": "Email is required"}), 400
    if role not in ["technician", "guard", "admin"]:
        return jsonify({"msg": "Invalid role"}), 400

    # Fetch user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    user.role = role  

    try:
        if role == "technician":
            skill_set = data.get("skill_set", "").strip()
            technician = Technician.query.filter_by(user_id=user.id).first()
            if not technician:
                technician = Technician(user_id=user.id, skill_set=skill_set)
                db.session.add(technician)
            else:
                technician.skill_set = skill_set  
        
        elif role == "guard":
            shift_start = data.get("shift_start", "").strip()
            shift_end = data.get("shift_end", "").strip()
            
            if not shift_start or not shift_end:
                return jsonify({"msg": "Shift start and end times are required for guards"}), 400

            guard = Guard.query.filter_by(user_id=user.id).first()
            if not guard:
                guard = Guard(user_id=user.id, shift_start=shift_start, shift_end=shift_end)
                db.session.add(guard)
            else:
                guard.shift_start = shift_start  
                guard.shift_end = shift_end

        db.session.commit()
        return jsonify({"msg": f"User promoted to {role} successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error promoting user: {str(e)}"}), 500


