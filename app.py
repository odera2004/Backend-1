from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta
from models import db, TokenBlocklist


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


migrate = Migrate(app, db)
db.init_app(app)

app.config["JWT_SECRET_KEY"] = "vghsdvvsjvy436u4wu37118gcd#"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] =  timedelta(hours=1)
jwt = JWTManager(app)
jwt.init_app(app)

from views import *

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(technician_bp)
app.register_blueprint(guard_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(auth_bp)



@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


# if __name__ == "__main__":
#     app.run(debug=True)
