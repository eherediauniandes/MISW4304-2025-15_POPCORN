from flask import Flask, Blueprint
from flask_restful import Api

from .api.config import config_by_name
from .api.extensions import db, jwt
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
    jwt.init_app(app)

    app.register_blueprint(create_api_blueprint())

    @app.get("/ping")
    def ping():
        return "pong", 200

    # ========================================
    # ENDPOINTS TEMPORALES PARA TESTING DE NEW RELIC
    # ========================================

    @app.get("/test/error-500")
    def test_error_500():
        """Endpoint temporal para generar un error 500 intencional"""
        raise Exception("Error 500 intencional para testing de New Relic - División por cero simulada")

    @app.get("/test/error-db")
    def test_error_db():
        """Endpoint temporal para generar un error de base de datos"""
        from .api.extensions import db
        # Intentar ejecutar una query inválida
        db.session.execute("SELECT * FROM tabla_que_no_existe")
        return "No debería llegar aquí", 200

    @app.get("/test/error-timeout")
    def test_error_timeout():
        """Endpoint temporal para simular un timeout/proceso lento"""
        import time
        time.sleep(10)  # Simular proceso muy lento
        return "Proceso completado después de 10 segundos", 200

    @app.get("/test/error-memory")
    def test_error_memory():
        """Endpoint temporal para simular un error de memoria"""
        # Intentar crear una lista gigante
        huge_list = [i for i in range(10**8)]
        return f"Lista creada con {len(huge_list)} elementos", 200

    return app
