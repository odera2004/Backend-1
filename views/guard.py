from flask import Blueprint, request, jsonify
from models import db, Guard

guard_bp = Blueprint('guard_bp', __name__)

# Add a guard
@guard_bp.route("/guard", methods=["POST"])
def add_guard():
    data = request.get_json()
    user_id = data['user_id']
    shift_start = data['shift_start']
    shift_end = data['shift_end']
    
    guard = Guard(user_id=user_id, shift_start=shift_start, shift_end=shift_end)
    db.session.add(guard)
    db.session.commit()
    return jsonify({'msg': 'Guard created successfully'}), 201

# Fetch all guards
@guard_bp.route("/guards", methods=["GET"])
def get_guards():
    guards = Guard.query.all()
    output = []
    for guard in guards:
        output.append({
            'id': guard.id,
            'user_id': guard.user_id,
            'first_name': guard.user.first_name,  # ✅ Fetch from User
            'last_name': guard.user.last_name,    # ✅ Fetch from User
            'email': guard.user.email,           # ✅ Fetch from User
            'shift_start': guard.shift_start,
            'shift_end': guard.shift_end,
            'role': 'Guard'
        })
    return jsonify(output), 200


# Fetch a guard by ID
@guard_bp.route("/guards/<int:guard_id>", methods=["GET"])
def get_guard(guard_id):
    guard = Guard.query.get(guard_id)
    if guard:
        return jsonify({
            'id': guard.id,
            'user_id': guard.user_id,
            'shift_start': guard.shift_start,
            'shift_end': guard.shift_end
        }), 200
    else:
        return jsonify({'msg': 'Guard not found'}), 404

# Update a guard
@guard_bp.route("/guards/<int:guard_id>", methods=["PUT"])
def update_guard(guard_id):
    data = request.get_json()
    guard = Guard.query.get(guard_id)

    if guard:
        guard.shift_start = data.get('shift_start', guard.shift_start)
        guard.shift_end = data.get('shift_end', guard.shift_end)
        db.session.commit()
        return jsonify({'msg': 'Guard updated successfully'}), 200
    else:
        return jsonify({'msg': 'Guard not found'}), 404

# Delete a guard
@guard_bp.route("/guards/<int:guard_id>", methods=["DELETE"])
def delete_guard(guard_id):
    guard = Guard.query.get(guard_id)
    if guard:
        db.session.delete(guard)
        db.session.commit()
        return jsonify({'msg': 'Guard deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Guard not found'}), 404