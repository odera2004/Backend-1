from flask import Blueprint, request, jsonify
from models import db, WorkOrder, Technician, User, WorkOrderPart, Part
from flask_jwt_extended import jwt_required, get_jwt_identity

work_order_bp = Blueprint('work_order_bp', __name__)

# Function to check if the user is a technician
def check_if_technician():
    user_id = get_jwt_identity()  # Get user id from the JWT token
    user = User.query.get(user_id)  # Fetch the user from the database
    if user and user.technician:  # Check if the user is a technician
        return True
    return False

# Add a new work order (Technician or Admin can create a work order)
@work_order_bp.route("/work_order", methods=["POST"])
@jwt_required()  # Ensure the user is authenticated
def add_work_order():
    data = request.get_json()
    
    # Ensure the user is authenticated and authorized as a technician or admin
    if not check_if_technician():
        return jsonify({'msg': 'Only technicians can create a work order'}), 403

    description = data['description']
    status = data.get('status', 'Pending')
    technician_id = data.get('technician_id')

    # Creating the work order
    new_work_order = WorkOrder(description=description, status=status, technician_id=technician_id)
    db.session.add(new_work_order)
    db.session.commit()

    return jsonify({'msg': 'Work order created successfully'}), 201

# Fetch all work orders (Any authenticated user can view)
@work_order_bp.route("/work_orders", methods=["GET"])
@jwt_required()  # Ensure the user is authenticated
def get_work_orders():
    work_orders = WorkOrder.query.all()
    output = []
    for work_order in work_orders:
        output.append({
            'id': work_order.id,
            'description': work_order.description,
            'status': work_order.status,
            'created_at': work_order.created_at,
            'technician_id': work_order.technician_id,
            'guard_id': work_order.guard_id,
        })
    return jsonify(output), 200

# Fetch a specific work order by ID (Any authenticated user can view)
@work_order_bp.route("/work_orders/<int:work_order_id>", methods=["GET"])
@jwt_required()  # Ensure the user is authenticated
def get_work_order(work_order_id):
    work_order = WorkOrder.query.get(work_order_id)
    if work_order:
        return jsonify({
            'id': work_order.id,
            'description': work_order.description,
            'status': work_order.status,
            'created_at': work_order.created_at,
            'technician_id': work_order.technician_id,
            'guard_id': work_order.guard_id,
        }), 200
    else:
        return jsonify({'msg': 'Work order not found'}), 404

# Update a work order (Only Technician can edit their assigned work order)
@work_order_bp.route("/work_orders/<int:work_order_id>", methods=["PUT"])
@jwt_required()  # Ensure the user is authenticated
def update_work_order(work_order_id):
    if not check_if_technician():
        return jsonify({'msg': 'Only technicians can update a work order'}), 403

    data = request.get_json()
    work_order = WorkOrder.query.get(work_order_id)

    if work_order:
        # Only allow the technician to edit their own assigned work order
        user_id = get_jwt_identity()
        technician = Technician.query.filter_by(user_id=user_id).first()
        if work_order.technician_id != technician.id:
            return jsonify({'msg': 'You can only edit your own assigned work orders'}), 403

        work_order.description = data.get('description', work_order.description)
        work_order.status = data.get('status', work_order.status)
        
        db.session.commit()
        return jsonify({'msg': 'Work order updated successfully'}), 200
    else:
        return jsonify({'msg': 'Work order not found'}), 404

# Delete a work order (Only Technician can delete their assigned work order)
@work_order_bp.route("/work_orders/<int:work_order_id>", methods=["DELETE"])
@jwt_required()  # Ensure the user is authenticated
def delete_work_order(work_order_id):
    if not check_if_technician():
        return jsonify({'msg': 'Only technicians can delete a work order'}), 403

    work_order = WorkOrder.query.get(work_order_id)

    if work_order:
        # Only allow the technician to delete their own assigned work order
        user_id = get_jwt_identity()
        technician = Technician.query.filter_by(user_id=user_id).first()
        if work_order.technician_id != technician.id:
            return jsonify({'msg': 'You can only delete your own assigned work orders'}), 403

        db.session.delete(work_order)
        db.session.commit()
        return jsonify({'msg': 'Work order deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Work order not found'}), 404

# Add parts to a work order (Only Technician can add parts)
@work_order_bp.route("/work_orders/<int:work_order_id>/parts", methods=["POST"])
@jwt_required()  # Ensure the user is authenticated
def add_parts_to_work_order(work_order_id):
    if not check_if_technician():
        return jsonify({'msg': 'Only technicians can add parts to a work order'}), 403

    data = request.get_json()
    quantity = data['quantity']
    part_id = data['part_id']

    # Check if the part exists
    part = Part.query.get(part_id)
    if not part:
        return jsonify({'msg': 'Part not found'}), 404

    # Create the WorkOrderPart
    new_work_order_part = WorkOrderPart(work_order_id=work_order_id, part_id=part_id, quantity=quantity)
    db.session.add(new_work_order_part)
    db.session.commit()

    return jsonify({'msg': 'Part added to work order successfully'}), 201