from flask import Blueprint, request, jsonify
from models import db, Vehicle

vehicle_bp = Blueprint('vehicle_bp', __name__)

# Create a new vehicle
@vehicle_bp.route('/vehicles', methods=['POST'])
def create_vehicle():
    data = request.get_json()
    if not data or 'number_plate' not in data or 'car_model' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_vehicle = Vehicle(
        number_plate=data['number_plate'],
        car_model=data['car_model']
    )
    db.session.add(new_vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle created successfully', 'vehicle': {
        'id': new_vehicle.id,
        'number_plate': new_vehicle.number_plate,
        'car_model': new_vehicle.car_model
    }}), 201

# Retrieve all vehicles
@vehicle_bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([{
        'id': v.id,
        'number_plate': v.number_plate,
        'car_model': v.car_model
    } for v in vehicles])

# Retrieve a single vehicle by ID
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    return jsonify({
        'id': vehicle.id,
        'number_plate': vehicle.number_plate,
        'car_model': vehicle.car_model
    })

# Update a vehicle
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    data = request.get_json()
    vehicle.number_plate = data.get('number_plate', vehicle.number_plate)
    vehicle.car_model = data.get('car_model', vehicle.car_model)
    
    db.session.commit()
    return jsonify({'message': 'Vehicle updated successfully'})

# Delete a vehicle
@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle deleted successfully'})