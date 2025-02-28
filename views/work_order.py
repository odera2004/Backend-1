from flask import Blueprint, request, jsonify
from models import db, WorkOrder, Technician, User, WorkOrderPart, Part,Vehicle

work_order_bp = Blueprint('work_order_bp', __name__)

# Add a new work order
@work_order_bp.route("/work_order", methods=["POST"])
def add_work_order():
    data = request.get_json()
    
    description = data['description']
    status = data.get('status', 'Pending')  
    technician_id = data.get('technician_id')
    guard_id = data.get('guard_id')
    vehicle_id = data.get('vehicle_id')

    new_work_order = WorkOrder(
        description=description, 
        status=status, 
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
            'guard_id': work_order.guard_id,
            'vehicle_number_plate': vehicle_number_plate  
        })

    return jsonify(output), 200


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


