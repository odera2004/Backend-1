from flask import Blueprint, request, jsonify
from models import db, Billing, WorkOrder
from datetime import datetime

billing_bp = Blueprint('billing_bp', __name__)

# Add a new billing
@billing_bp.route("/billing", methods=["POST"])
def add_billing():
    data = request.get_json()
    total_amount = data['total_amount']
    due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
    work_order_id = data['work_order_id']
    payment_status = data.get('payment_status', 'Pending') 

    # Handle optional payment_date
    payment_date = None
    if data.get("payment_date"):  
        payment_date = datetime.strptime(data["payment_date"], "%Y-%m-%d")

    # Ensure work order exists
    work_order = WorkOrder.query.get(work_order_id)
    if not work_order:
        return jsonify({'msg': 'Work order not found'}), 404

    # Create a new billing entry
    new_billing = Billing(
        total_amount=total_amount,
        due_date=due_date,
        payment_date=payment_date, 
        payment_status=payment_status,
        work_order_id=work_order_id
    )

    db.session.add(new_billing)
    db.session.commit()

    return jsonify({'msg': 'Billing created successfully'}), 201

# Fetch all billings
@billing_bp.route("/billings", methods=["GET"])
def get_billings():
    billings = Billing.query.all()
    output = []
    for billing in billings:
        output.append({
            'id': billing.id,
            'total_amount': billing.total_amount,
            'due_date': billing.due_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'payment_date': billing.payment_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'payment_status': billing.payment_status,
            'work_order_id': billing.work_order_id
        })
    return jsonify(output), 200

# Fetch a single billing by ID
@billing_bp.route("/billings/<int:billing_id>", methods=["GET"])
def get_billing(billing_id):
    billing = Billing.query.get(billing_id)
    if billing:
        return jsonify({
            'id': billing.id,
            'total_amount': billing.total_amount,
            'due_date': billing.due_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'payment_date': billing.payment_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'payment_status': billing.payment_status,
            'work_order_id': billing.work_order_id
        }), 200
    else:
        return jsonify({'msg': 'Billing not found'}), 404

# Update a billing
@billing_bp.route("/billings/<int:billing_id>", methods=["PUT"])
def update_billing(billing_id):
    data = request.get_json()
    billing = Billing.query.get(billing_id)

    if billing:
        billing.total_amount = data.get('total_amount', billing.total_amount)
        billing.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
        billing.payment_date = datetime.strptime(data["payment_date"], "%Y-%m-%d")
        billing.payment_status = data.get('payment_status', billing.payment_status)
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

# Delete a billing
@billing_bp.route("/billings/<int:billing_id>", methods=["DELETE"])
def delete_billing(billing_id):
    billing = Billing.query.get(billing_id)
    if billing:
        db.session.delete(billing)
        db.session.commit()
        return jsonify({'msg': 'Billing deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Billing not found'}), 404
