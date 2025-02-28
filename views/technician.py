from flask import Blueprint, request, jsonify
from models import db, Technician

technician_bp = Blueprint('technician_bp', __name__)

# Add a technician
@technician_bp.route("/technician", methods=["POST"])
def add_technician():
    data = request.get_json()
    user_id = data['user_id']
    skill_set = data.get('skill_set')
    
    technician = Technician(user_id=user_id, skill_set=skill_set)
    db.session.add(technician)
    db.session.commit()
    return jsonify({'msg': 'Technician created successfully'}), 201

# Fetch all technicians
@technician_bp.route("/technicians", methods=["GET"])
def get_technicians():
    technicians = Technician.query.all()
    output = []
    for technician in technicians:
        output.append({
            'id': technician.id,
            'user_id': technician.user_id,
            'first_name': technician.user.first_name,  # ✅ Fetch from User
            'last_name': technician.user.last_name,    # ✅ Fetch from User
            'email': technician.user.email,           # ✅ Fetch from User
            'skill_set': technician.skill_set,
            'role': 'Technician'
        })
    return jsonify(output), 200


# Fetch a technician by ID
@technician_bp.route("/technicians/<int:technician_id>", methods=["GET"])
def get_technician(technician_id):
    technician = Technician.query.get(technician_id)
    if technician:
        return jsonify({
            'id': technician.id,
            'user_id': technician.user_id,
            'skill_set': technician.skill_set,
            'active': technician.active
        }), 200
    else:
        return jsonify({'msg': 'Technician not found'}), 404

# Update a technician
@technician_bp.route("/technicians/<int:technician_id>", methods=["PUT"])
def update_technician(technician_id):
    data = request.get_json()
    technician = Technician.query.get(technician_id)

    if technician:
        technician.skill_set = data.get('skill_set', technician.skill_set)
        technician.active = data.get('active', technician.active)
        db.session.commit()
        return jsonify({'msg': 'Technician updated successfully'}), 200
    else:
        return jsonify({'msg': 'Technician not found'}), 404

# Delete a technician
@technician_bp.route("/technicians/<int:technician_id>", methods=["DELETE"])
def delete_technician(technician_id):
    technician = Technician.query.get(technician_id)
    if technician:
        db.session.delete(technician)
        db.session.commit()
        return jsonify({'msg': 'Technician deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Technician not found'}), 404