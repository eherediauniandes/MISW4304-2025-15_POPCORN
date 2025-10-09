from flask import Flask, Blueprint
from flask_restful import Api

from .api.config import config_by_name
from .api.extensions import db
from .api.routes import register_resources

def create_api_blueprint() -> Blueprint:
    
    bp = Blueprint("api_root", __name__) 
    api = Api(bp)
    register_resources(api)
    return bp

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)

    app.register_blueprint(create_api_blueprint())

    @app.get("/ping")
    def ping():
        return "pong", 200

    return app
