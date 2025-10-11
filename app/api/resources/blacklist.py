from flask_restful import Resource
from ..auth import static_bearer_required
from ...services.blacklist_create_service import BlacklistCreateService
from ...services.blacklist_get_service import BlacklistGetService

class BlacklistCreateResource(Resource):

    @static_bearer_required
    def post(self):
        #TODO: Implementar la lógica para crear un nuevo elemento en la lista negra
        return {}, 201

class BlacklistGetResource(Resource):

    @static_bearer_required
    def get(self, email: str):
        """
        Obtiene información sobre si un email está en la blacklist
        
        Args:
            email (str): Email a consultar en la blacklist
            
        Returns:
            dict: Solo is_blocked (boolean) y blocked_reason (si está bloqueado)
        """
        try:
            # Procesar la consulta a través del servicio
            result = BlacklistGetService.get_blacklist_by_email(email)
            
            # Respuesta exitosa - retorna directamente los datos del servicio
            return result, HTTPStatus.OK
            
        except ValueError as e:
            # Error de validación
            return {'error': str(e)}, HTTPStatus.BAD_REQUEST
            
        except Exception as e:
            # Error interno del servidor
            return {'error': 'Error interno del servidor'}, HTTPStatus.INTERNAL_SERVER_ERROR
