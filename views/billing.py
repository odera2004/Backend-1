from flask import Blueprint, request, jsonify
from models import db, Billing, WorkOrder, User
from flask_jwt_extended import jwt_required, get_jwt_identity

billing_bp = Blueprint('billing_bp', __name__)

# Function to check if the user is an admin
def check_if_admin():
    user_id = get_jwt_identity()  # Get user id from the JWT token
    user = User.query.get(user_id)  # Fetch the user from the database
    if user and user.is_admin:
        return True
    return False

# Add a new billing (Only Admin)
@billing_bp.route("/billing", methods=["POST"])
@jwt_required()  # Ensure the user is authenticated
def add_billing():
    if not check_if_admin():
        return jsonify({'msg': 'You are not authorized to perform this action'}), 403

    data = request.get_json()
    total_amount = data['total_amount']
    due_date = data['due_date']
    work_order_id = data['work_order_id']
    
    # Ensure work order exists
    work_order = WorkOrder.query.get(work_order_id)
    if not work_order:
        return jsonify({'msg': 'Work order not found'}), 404

    # Create a new billing entry
    new_billing = Billing(total_amount=total_amount, due_date=due_date, work_order_id=work_order_id)
    db.session.add(new_billing)
    db.session.commit()

    return jsonify({'msg': 'Billing created successfully'}), 201

# Fetch all billings (Only Admin)
@billing_bp.route("/billings", methods=["GET"])
@jwt_required()  # Ensure the user is authenticated
def get_billings():
    if not check_if_admin():
        return jsonify({'msg': 'You are not authorized to perform this action'}), 403

    billings = Billing.query.all()
    output = []
    for billing in billings:
        output.append({
            'id': billing.id,
            'total_amount': billing.total_amount,
            'due_date': billing.due_date,
            'work_order_id': billing.work_order_id
        })
    return jsonify(output), 200

# Fetch a single billing by ID (Only Admin)
@billing_bp.route("/billings/<int:billing_id>", methods=["GET"])
@jwt_required()  # Ensure the user is authenticated
def get_billing(billing_id):
    if not check_if_admin():
        return jsonify({'msg': 'You are not authorized to perform this action'}), 403

    billing = Billing.query.get(billing_id)
    if billing:
        return jsonify({
            'id': billing.id,
            'total_amount': billing.total_amount,
            'due_date': billing.due_date,
            'work_order_id': billing.work_order_id
        }), 200
    else:
        return jsonify({'msg': 'Billing not found'}), 404

# Update a billing (Only Admin)
@billing_bp.route("/billings/<int:billing_id>", methods=["PUT"])
@jwt_required()  # Ensure the user is authenticated
def update_billing(billing_id):
    if not check_if_admin():
        return jsonify({'msg': 'You are not authorized to perform this action'}), 403

    data = request.get_json()
    billing = Billing.query.get(billing_id)

    if billing:
        billing.total_amount = data.get('total_amount', billing.total_amount)
        billing.due_date = data.get('due_date', billing.due_date)
        billing.work_order_id = data.get('work_order_id', billing.work_order_id)
        
        # Ensure work order exists
        if billing.work_order_id:
            work_order = WorkOrder.query.get(billing.work_order_id)
            if not work_order:
                return jsonify({'msg': 'Work order not found'}), 404

        db.session.commit()
        return jsonify({'msg': 'Billing updated successfully'}), 200
    else:
        return jsonify({'msg': 'Billing not found'}), 404

# Delete a billing (Only Admin)
@billing_bp.route("/billings/<int:billing_id>", methods=["DELETE"])
@jwt_required()  # Ensure the user is authenticated
def delete_billing(billing_id):
    if not check_if_admin():
        return jsonify({'msg': 'You are not authorized to perform this action'}), 403

    billing = Billing.query.get(billing_id)
    if billing:
        db.session.delete(billing)
        db.session.commit()
        return jsonify({'msg': 'Billing deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Billing not found'}), 404