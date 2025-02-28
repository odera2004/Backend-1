from flask import Blueprint, request, jsonify
from models import db, Part

parts_bp = Blueprint('parts_bp', __name__)

# Add a new part
@parts_bp.route("/parts", methods=["POST"])
def add_part():
    data = request.get_json()
    name = data.get('name')
    quantity = data.get('quantity')
    price = data.get('price')
    
    if not all([name, quantity, price]):
        return jsonify({'msg': 'Missing required fields'}), 400
    
    part = Part(name=name, quantity=quantity, price=price)
    db.session.add(part)
    db.session.commit()
    
    return jsonify({'msg': 'Part created successfully'}), 201

# Fetch all parts
@parts_bp.route("/parts", methods=["GET"])
def get_parts():
    parts = Part.query.all()
    output = [{
        'id': part.id,
        'name': part.name,
        'quantity': part.quantity,
        'price': part.price
    } for part in parts]
    
    return jsonify(output), 200

# Fetch a part by ID
@parts_bp.route("/parts/<int:part_id>", methods=["GET"])
def get_part(part_id):
    part = Part.query.get(part_id)
    if part:
        return jsonify({
            'id': part.id,
            'name': part.name,
            'quantity': part.quantity,
            'price': part.price
        }), 200
    else:
        return jsonify({'msg': 'Part not found'}), 404

# Update a part
@parts_bp.route("/parts/<int:part_id>", methods=["PUT"])
def update_part(part_id):
    data = request.get_json()
    part = Part.query.get(part_id)
    
    if part:
        part.name = data.get('name', part.name)
        part.quantity = data.get('quantity', part.quantity)
        part.price = data.get('price', part.price)
        db.session.commit()
        return jsonify({'msg': 'Part updated successfully'}), 200
    else:
        return jsonify({'msg': 'Part not found'}), 404

# Delete a part
@parts_bp.route("/parts/<int:part_id>", methods=["DELETE"])
def delete_part(part_id):
    part = Part.query.get(part_id)
    if part:
        db.session.delete(part)
        db.session.commit()
        return jsonify({'msg': 'Part deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Part not found'}), 404
