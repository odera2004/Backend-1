from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message
from flask_cors import CORS  # Import CORS
from datetime import timedelta
from flask_cors import CORS  # Import CORS
from models import db, TokenBlocklist
import os


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://automation_70iv_user:wMu3HipM5SQAn3P6xfZC7oUyQZmI2m4K@dpg-cuvh1ia3esus73bqd8a0-a.oregon-postgres.render.com/automation_70iv'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


migrate = Migrate(app, db)
db.init_app(app)

app.config["JWT_SECRET_KEY"] = "vghsdvvsjvy436u4wu37118gcd#"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] =  timedelta(hours=1)
jwt = JWTManager(app)
jwt.init_app(app)


# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'eugine.odera@student.moringaschool.com'  # Use a simpler environment variable key
app.config['MAIL_PASSWORD'] ='xcac bhny cgkg wbhd'  # Use a simpler environment variable key
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']  # Default sender

mail = Mail(app)

@app.route("/")
def index():
    try:
        msg = Message(
            subject='Hello from the other side!',
            sender=app.config['MAIL_USERNAME'],  # Explicit sender
            recipients=['eugeneodera59@gmail.com']
        )
        msg.body = "Hey Samson, sending you this email from my Flask app, lmk if it works."
        mail.send(msg)
        return "Message sent successfully!"
    except Exception as e:
        return f"An error occurred: {e}"

from views import *

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(guard_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(vehicle_bp)
app.register_blueprint(technician_bp)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(work_order_bp, url_prefix="/api")
app.register_blueprint(parts_bp, url_prefix="/admin")


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


# if __name__ == "__main__":
#     app.run(debug=True)
