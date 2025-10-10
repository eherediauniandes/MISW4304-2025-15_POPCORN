from flask_restful import Resource
from flask import request
from sqlalchemy.exc import IntegrityError
from http import HTTPStatus
from ..auth import static_bearer_required
from ..extensions import db
from ...models.blacklist import Blacklist
import uuid


def get_client_ip():
    """Obtiene la dirección IP del cliente, considerando proxies y load balancers"""
    # Lista de headers que pueden contener la IP real del cliente
    ip_headers = [
        'X-Forwarded-For',      # Estándar para proxies y load balancers
        'X-Real-IP',            # Nginx y otros proxies
        'X-Forwarded-Proto',    # Protocolo usado (contiene IP en algunos casos)
        'CF-Connecting-IP',     # Cloudflare
        'True-Client-IP',       # Akamai
        'X-Cluster-Client-IP',  # Load balancers en clusters
        # AWS Headers
        'X-Amzn-Trace-Id',      # AWS Application Load Balancer
        'X-Forwarded-Port',     # AWS ALB/ELB (puede incluir IP)
        'X-Amz-Cf-Id'           # AWS CloudFront
    ]
    
    # Verificar cada header en orden de prioridad
    for header in ip_headers:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For puede contener múltiples IPs separadas por comas
            # La primera es la IP original del cliente
            return ip.split(',')[0].strip()
    
    # Si no hay headers de proxy, usar la IP remota directa
    return request.environ.get('REMOTE_ADDR', 'unknown')

class BlacklistCreateResource(Resource):

    @static_bearer_required
    def post(self):
        try:
            # Obtener datos del request
            data = request.get_json()
            
            # Validar que los campos requeridos estén presentes
            if not data:
                return {'error': 'No se proporcionaron datos'}, HTTPStatus.BAD_REQUEST
            
            email = data.get('email')
            app_uuid = data.get('app_uuid')
            blocked_reason = data.get('blocked_reason')
            
            # Validaciones
            if not email:
                return {'error': 'El campo email es requerido'}, HTTPStatus.BAD_REQUEST
            
            if not app_uuid:
                return {'error': 'El campo app_uuid es requerido'}, HTTPStatus.BAD_REQUEST
            
            # Validar formato UUID
            try:
                uuid.UUID(app_uuid)
            except ValueError:
                return {'error': 'El app_uuid debe ser un UUID válido'}, HTTPStatus.BAD_REQUEST
            
            # Verificar si el email ya existe en la blacklist
            existing_blacklist = Blacklist.query.filter_by(email=email).first()
            if existing_blacklist:
                return {'error': 'El email ya está en la lista negra'}, HTTPStatus.CONFLICT
            
            # Obtener la IP del cliente
            client_ip = get_client_ip()
            
            # Crear nuevo elemento en la blacklist
            new_blacklist = Blacklist(
                email=email,
                app_uuid=app_uuid,
                blocked_reason=blocked_reason,
                ip_address=client_ip
            )
            
            # Guardar en la base de datos
            db.session.add(new_blacklist)
            db.session.commit()
            
            return {
                'message': 'Email agregado a la lista negra exitosamente',
                'data': {
                    'email': new_blacklist.email,
                    'app_uuid': new_blacklist.app_uuid,
                    'blocked_reason': new_blacklist.blocked_reason,
                    'ip_address': new_blacklist.ip_address
                }
            }, HTTPStatus.CREATED
            
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Error de integridad en la base de datos'}, HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            db.session.rollback()
            return {'error': f'Error interno del servidor: {str(e)}'}, HTTPStatus.INTERNAL_SERVER_ERROR

class BlacklistGetResource(Resource):

    @static_bearer_required
    def get(self, email: str):
        #TODO: Implementar la lógica para obtener un elemento específico de la lista negra
        return {}, 200
