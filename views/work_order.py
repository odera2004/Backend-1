from flask import Blueprint, request, jsonify
from models import db, WorkOrder, Technician, User,Billing

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
    number_plate = data.get('number_plate')

    new_work_order = WorkOrder(
        description=description,
        status=status,
        user_id=user_id,
        technician_id=technician_id,
        guard_id=guard_id,
        number_plate=number_plate
    )
    db.session.add(new_work_order)
    db.session.commit()

    return jsonify({'msg': 'Work order created successfully'}), 201


# Fetch all work orders
@work_order_bp.route("/work_orders", methods=["GET"])
def get_work_orders():
    user_id = request.args.get('user_id') 
    status_filter = request.args.get('status') 

    # Base query
    query = WorkOrder.query

    # Apply user filter (only fetch work orders for the current user)
    if user_id:
        query = query.filter_by(user_id=user_id)

    # Apply status filter
    if status_filter:
        if status_filter == 'active':
            query = query.filter(WorkOrder.status.in_(['Pending', 'in progress']))
        elif status_filter == 'previous':
            query = query.filter_by(status='completed')

    work_orders = query.all()

    output = []

    for work_order in work_orders:
        # Fetch technician details
        technician = Technician.query.get(work_order.technician_id)
        technician_name = f"{technician.user.first_name} {technician.user.last_name}" if technician else "Unknown Technician"


        output.append({
            'id': work_order.id,
            'description': work_order.description,
            'status': work_order.status,
            'created_at': work_order.created_at,
            'technician': technician_name,
            'technician_id': work_order.technician_id,  
            'guard_id': work_order.guard_id,
            'number_plate':work_order.number_plate
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
    
#Fetch User ID by email
@work_order_bp.route("/users/email/<email>", methods=["GET"])
def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'id': user.id}), 200
    else:
        return jsonify({'msg': 'User not found'}), 404
 
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
            'number_plate':work_order.number_plate,
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
    
#Verification for checkout clearance  
@work_order_bp.route('/checkout', methods=['POST'])
def security_checkout():
    data = request.get_json()
    number_plate = data.get("number_plate")

    if not number_plate:
        return jsonify({"error": "Vehicle number plate is required"}), 400

    # Find the work order by number plate
    work_order = WorkOrder.query.filter_by(number_plate=number_plate).first()

    if not work_order:
        return jsonify({"status": "Error", "message": "Vehicle not found"}), 404

    # Check if there's any pending work order for this vehicle
    pending_work_order = WorkOrder.query.filter_by(number_plate=number_plate, status="Pending").first()

    if pending_work_order:
        # Check if a billing record exists for this work order
        billing = Billing.query.filter_by(work_order_id=pending_work_order.id).first()

        if not billing:
            return jsonify({
                "status": "Error",
                "message": f"No billing record found for Work Order #{pending_work_order.id}. Cannot checkout."
            }), 403

        # Check if the billing record has a pending payment
        if billing.payment_status == "Pending":
            return jsonify({
                "status": "Pending",
                "message": f"Cannot checkout. Clear pending bill for Work Order #{pending_work_order.id}"
            }), 403

    return jsonify({
        "status": "Cleared",
        "message": "Vehicle is cleared for checkout"
    }), 200
