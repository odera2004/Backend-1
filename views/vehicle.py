from flask import Blueprint, request, jsonify
from models import db, Vehicle,WorkOrder,Billing

vehicle_bp = Blueprint('vehicle_bp', __name__)

@vehicle_bp.route("/vehicle", methods=["POST"])
def add_vehicle():
    data = request.get_json()
    number_plate = data.get('number_plate')
    car_model = data.get('car_model')
    user_id = data.get('user_id')  
    
    if not all([number_plate, car_model, user_id]): 
        return jsonify({'msg': 'Missing required fields'}), 400

    vehicle = Vehicle(number_plate=number_plate, car_model=car_model, user_id=user_id)
    db.session.add(vehicle)
    db.session.commit()
    
    return jsonify({'msg': 'Vehicle created successfully'}), 201

# Fetch all vehicles
@vehicle_bp.route("/vehicles", methods=["GET"])
def get_vehicles():
    vehicles = Vehicle.query.all()
    output = []
    for vehicle in vehicles:
        output.append({
            'id': vehicle.id,
            'number_plate': vehicle.number_plate,
            'car_model': vehicle.car_model
        })
    return jsonify(output), 200

# Fetch a vehicle by ID
@vehicle_bp.route("/vehicles/<int:vehicle_id>", methods=["GET"])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle:
        return jsonify({
            'id': vehicle.id,
            'number_plate': vehicle.number_plate,
            'car_model': vehicle.car_model
        }), 200
    else:
        return jsonify({'msg': 'Vehicle not found'}), 404

# Update a vehicle
@vehicle_bp.route("/vehicles/<int:vehicle_id>", methods=["PUT"])
def update_vehicle(vehicle_id):
    data = request.get_json()
    vehicle = Vehicle.query.get(vehicle_id)
    
    if vehicle:
        vehicle.number_plate = data.get('number_plate', vehicle.number_plate)
        vehicle.car_model = data.get('car_model', vehicle.car_model)
        db.session.commit()
        return jsonify({'msg': 'Vehicle updated successfully'}), 200
    else:
        return jsonify({'msg': 'Vehicle not found'}), 404

# Delete a vehicle
@vehicle_bp.route("/vehicles/<int:vehicle_id>", methods=["DELETE"])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle:
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({'msg': 'Vehicle deleted successfully'}), 200
    else:
        return jsonify({'msg': 'Vehicle not found'}), 404
    
#Security Checkout
@vehicle_bp.route('/checkout', methods=['POST'])
def security_checkout():
    data = request.get_json()
    vehicle_plate = data.get("vehicle_plate")

    if not vehicle_plate:
        return jsonify({"error": "Vehicle plate is required"}), 400

    # Step 1: Find the vehicle by number plate
    vehicle = Vehicle.query.filter_by(number_plate=vehicle_plate).first()  # Use number_plate

    if not vehicle:
        return jsonify({"status": "Error", "message": "Vehicle not found"}), 404

    # Step 2: Check if there's any pending Work Order for this vehicle
    pending_work_order = WorkOrder.query.filter_by(vehicle_id=vehicle.id, status="Pending").first()

    if pending_work_order:
        # Step 3: Check if this work order has a pending bill
        pending_bill = Billing.query.filter_by(work_order_id=pending_work_order.id, payment_status="Pending").first()
        
        if pending_bill:
            return jsonify({
                "status": "Pending",
                "message": f"Cannot checkout. Clear pending bill for Work Order #{pending_work_order.id}"
            }), 403

    return jsonify({
        "status": "Cleared",
        "message": "Vehicle is cleared for checkout"
    }), 200
