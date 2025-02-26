from flask import Blueprint, request, jsonify
from models import db, WorkOrderPart, Part

workorderpart_bp = Blueprint('workorderpart_bp', __name__)

# Fetch all parts used in a specific work order
@workorderpart_bp.route("/workorder_parts/<int:work_order_id>", methods=["GET"])
def get_parts_by_work_order(work_order_id):
    work_order_parts = WorkOrderPart.query.filter_by(work_order_id=work_order_id).all()
    
    output = []
    for work_order_part in work_order_parts:
        part = Part.query.get(work_order_part.part_id)
        output.append({
            'id': work_order_part.id,
            'part_name': part.name if part else "Unknown",
            'quantity_used': work_order_part.quantity,
            'part_id': work_order_part.part_id
        })

    return jsonify(output), 200

# Add a new part to a work order and update stock
@workorderpart_bp.route("/workorder_parts", methods=["POST"])
def add_work_order_part():
    data = request.get_json()
    work_order_id = data['work_order_id']
    part_id = data['part_id']
    quantity_used = data['quantity']

    part = Part.query.get(part_id)
    if not part:
        return jsonify({'msg': 'Part not found'}), 404

    if part.quantity < quantity_used:
        return jsonify({'msg': 'Not enough stock available'}), 400

    # Deduct the quantity from the parts table
    part.quantity -= quantity_used

    # Create new work order part entry
    new_work_order_part = WorkOrderPart(work_order_id=work_order_id, part_id=part_id, quantity=quantity_used)
    db.session.add(new_work_order_part)
    db.session.commit()

    return jsonify({'msg': 'Part added to work order successfully, stock updated'}), 201
