from flask import Blueprint, request, jsonify
from models import db, WorkOrder, Technician, User, WorkOrderPart, Part,Vehicle

work_order_bp = Blueprint('work_order_bp', __name__)

# Add a new work order
@work_order_bp.route("/work_order", methods=["POST"])
def add_work_order():
    data = request.get_json()

    description = data['description']
    status = data.get('status', 'Pending')
    user_id =data.get('user_id')
    technician_id = data.get('technician_id')
    guard_id = data.get('guard_id')
    vehicle_id = data.get('vehicle_id')

    new_work_order = WorkOrder(
        description=description,
        status=status,
        user_id=user_id,
        technician_id=technician_id,
        guard_id=guard_id,
        vehicle_id=vehicle_id
    )
    db.session.add(new_work_order)
    db.session.commit()

    return jsonify({'msg': 'Work order created successfully'}), 201


# Fetch all work orders
@work_order_bp.route("/work_orders", methods=["GET"])
def get_work_orders():
    technician_id = request.args.get('technician_id')  

    if technician_id:
        work_orders = WorkOrder.query.filter_by(technician_id=technician_id).all()
    else:
        work_orders = WorkOrder.query.all()

    output = []

    for work_order in work_orders:
        # Fetch technician details
        technician = Technician.query.get(work_order.technician_id)
        technician_name = f"{technician.user.first_name} {technician.user.last_name}" if technician else "Unknown Technician"

        # Fetch vehicle details
        vehicle = Vehicle.query.get(work_order.vehicle_id)
        vehicle_number_plate = vehicle.number_plate if vehicle else "-"

        output.append({
            'id': work_order.id,
            'description': work_order.description,
            'status': work_order.status,
            'created_at': work_order.created_at,
            'technician': technician_name,
            'technician_id': work_order.technician_id,  
            'guard_id': work_order.guard_id,
            'vehicle_number_plate': vehicle_number_plate
        })

    return jsonify(output), 200

# Fetch Technician by User ID
@work_order_bp.route("/technician", methods=["GET"])
def get_technician_by_user_id():
    user_id = request.args.get('user_id')
    technician = Technician.query.filter_by(user_id=user_id).first()
    if technician:
        return jsonify({'id': technician.id}), 200
    else:
        return jsonify({'msg': 'Technician not found'}), 404

# Fetch a specific work order by ID
@work_order_bp.route("/work_orders/<int:work_order_id>", methods=["GET"])
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

# Update a work order
@work_order_bp.route("/work_orders/<int:work_order_id>", methods=["PUT"])
def update_work_order(work_order_id):
    data = request.get_json()
    work_order = WorkOrder.query.get(work_order_id)

    if work_order:
        work_order.description = data.get('description', work_order.description)
        work_order.status = data.get('status', work_order.status)
        
        db.session.commit()
        return jsonify({'msg': 'Work order updated successfully'}), 200
    else:
        return jsonify({'msg': 'Work order not found'}), 404

# Delete a work order
@work_order_bp.route("/work_order/<int:work_order_id>", methods=["DELETE"])
def delete_work_order(work_order_id):
    work_order = WorkOrder.query.get(work_order_id)

    if work_order:
        db.session.delete(work_order)
        db.session.commit()
        return jsonify({'msg': 'Work order deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Work order not found'}), 404

# Add parts to a work order
@work_order_bp.route("/work_orders/<int:work_order_id>/parts", methods=["POST"])
def add_parts_to_work_order(work_order_id):
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
