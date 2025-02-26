from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    profile_picture = db.Column(db.String(256), nullable=True, default="default.jpg")


# Relationship for technician, guard, admin
technician = db.relationship('Technician', backref='user', uselist=False)
guard = db.relationship('Guard', backref='user', uselist=False)
class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_set = db.Column(db.String(256), nullable=True)  # Skills the technician is trained in

work_orders = db.relationship("WorkOrder", backref="technician", lazy=True)
class Guard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shift_start = db.Column(db.String, nullable=False)
    shift_end = db.Column(db.String, nullable=False)

work_orders = db.relationship("WorkOrder", backref="guard", lazy=True)
class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# For tracking which work orders used this part
work_orders = db.relationship("WorkOrderPart", backref="part", lazy=True)
class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(64), default="Pending")
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    technician_id = db.Column(db.Integer, db.ForeignKey('technician.id'), nullable=True)
    guard_id = db.Column(db.Integer, db.ForeignKey('guard.id'), nullable=True)
    

# Relationships to other models
parts = db.relationship("WorkOrderPart", backref="work_order", lazy=True)
billing = db.relationship("Billing", backref="work_order", uselist=False)
class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_status = db.Column(db.String(64), default="Pending") 

    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
   

class WorkOrderPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String(128), nullable=False)
    car_model = db.Column(db.String(128), nullable=False)

user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
   
# TokenBlocklist for managing token revocation
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
