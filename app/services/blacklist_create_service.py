from flask import request
from sqlalchemy.exc import IntegrityError
from ..api.extensions import db
from ..models.blacklist import Blacklist
import uuid

class BlacklistCreateService:
    """Servicio para manejar la lógica de creación de elementos en la blacklist"""
    
    @staticmethod
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
    
    @staticmethod
    def validate_data(data):
        """Valida los datos de entrada para crear un elemento en la blacklist"""
        errors = []
        
        if not data:
            errors.append('No se proporcionaron datos')
            return errors
        
        email = data.get('email')
        app_uuid = data.get('app_uuid')
        
        # Validaciones de campos requeridos
        if not email:
            errors.append('El campo email es requerido')
        
        if not app_uuid:
            errors.append('El campo app_uuid es requerido')
        
        # Validar formato UUID si está presente
        if app_uuid:
            try:
                uuid.UUID(app_uuid)
            except ValueError:
                errors.append('El app_uuid debe ser un UUID válido')
        
        return errors
    
    @staticmethod
    def email_exists(email):
        """Verifica si un email ya existe en la blacklist"""
        return Blacklist.query.filter_by(email=email).first() is not None
    
    @staticmethod
    def create_blacklist_item(email, app_uuid, blocked_reason):
        """Crea un nuevo elemento en la blacklist"""
        try:
            # Obtener la IP del cliente
            client_ip = BlacklistCreateService.get_client_ip()
            
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
            
            return new_blacklist, None
            
        except IntegrityError as e:
            db.session.rollback()
            return None, 'Error de integridad en la base de datos'
        except Exception as e:
            db.session.rollback()
            return None, f'Error interno del servidor: {str(e)}'
    
    @classmethod
    def process_create_request(cls, data):
        """Procesa una petición completa de creación de blacklist"""
        # Validar datos
        validation_errors = cls.validate_data(data)
        if validation_errors:
            return {
                'success': False,
                'errors': validation_errors,
                'status_code': 400
            }
        
        email = data.get('email')
        app_uuid = data.get('app_uuid')
        blocked_reason = data.get('blocked_reason')
        
        # Verificar si el email ya existe
        if cls.email_exists(email):
            return {
                'success': False,
                'errors': ['El email ya está en la lista negra'],
                'status_code': 409
            }
        
        # Crear el elemento
        blacklist_item, error = cls.create_blacklist_item(email, app_uuid, blocked_reason)
        
        if error:
            return {
                'success': False,
                'errors': [error],
                'status_code': 500
            }
        
        return {
            'success': True,
            'data': blacklist_item,
            'message': 'Email agregado a la lista negra exitosamente',
            'status_code': 201
        }
