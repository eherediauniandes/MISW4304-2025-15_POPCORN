from flask import Flask, Blueprint
from flask_restful import Api
# from .api.routes import register_resources
from .api.config import config_by_name
from .api.extensions import db

def create_api_blueprint(url_prefix="/api/v1") -> Blueprint:
    
    bp = Blueprint("api_v1", __name__, url_prefix=url_prefix)
    api = Api(bp)  

    # register_resources(api)

    return bp

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)

    app.register_blueprint(create_api_blueprint(url_prefix="/api/v1"))

    @app.get("/ping")
    def ping():
        return {"status": "ok"}, 200

    return app
