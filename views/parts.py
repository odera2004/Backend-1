from flask import Blueprint, request, jsonify
from models import db, Part
from flask_jwt_extended import jwt_required

parts_bp = Blueprint('parts_bp', __name__)

# Create a new part
@parts_bp.route("/parts", methods=["POST"])
@jwt_required()
def add_part():
    data = request.get_json()
    name = data.get('name')
    quantity = data.get('quantity', 0)
    price = data.get('price')

    if not name or price is None:
        return jsonify({'msg': 'Name and price are required'}), 400

    new_part = Part(name=name, quantity=quantity, price=price)
    db.session.add(new_part)
    db.session.commit()

    return jsonify({'msg': 'Part added successfully'}), 201

# Get all parts
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

# Get a single part by ID
@parts_bp.route("/parts/<int:part_id>", methods=["GET"])
def get_part(part_id):
    part = Part.query.get(part_id)
    if not part:
        return jsonify({'msg': 'Part not found'}), 404

    return jsonify({
        'id': part.id,
        'name': part.name,
        'quantity': part.quantity,
        'price': part.price
    }), 200

# Update a part
@parts_bp.route("/parts/<int:part_id>", methods=["PUT"])
@jwt_required()
def update_part(part_id):
    part = Part.query.get(part_id)
    if not part:
        return jsonify({'msg': 'Part not found'}), 404

    data = request.get_json()
    part.name = data.get('name', part.name)
    part.quantity = data.get('quantity', part.quantity)
    part.price = data.get('price', part.price)

    db.session.commit()
    return jsonify({'msg': 'Part updated successfully'}), 200

# Delete a part
@parts_bp.route("/parts/<int:part_id>", methods=["DELETE"])
@jwt_required()
def delete_part(part_id):
    part = Part.query.get(part_id)
    if not part:
        return jsonify({'msg': 'Part not found'}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({'msg': 'Part deleted successfully'}), 200
