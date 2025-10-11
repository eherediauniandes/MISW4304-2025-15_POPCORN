from flask_restful import Resource
from flask import request
from http import HTTPStatus
from ..auth import static_bearer_required
from ...services.blacklist_create_service import BlacklistCreateService

class BlacklistCreateResource(Resource):

    @static_bearer_required
    def post(self):
        # Obtener datos del request
        data = request.get_json()
        
        # Procesar la petición a través del servicio
        result = BlacklistCreateService.process_create_request(data)
        
        if not result['success']:
            # Manejar errores
            error_message = result['errors'][0] if len(result['errors']) == 1 else result['errors']
            return {'error': error_message}, result['status_code']
        
        # Respuesta exitosa
        return {
            'message': result['message'],
            'data': {
                'email': result['data'].email,
                'app_uuid': result['data'].app_uuid,
                'blocked_reason': result['data'].blocked_reason,
                'ip_address': result['data'].ip_address
            }
        }, result['status_code']

class BlacklistGetResource(Resource):

    @static_bearer_required
    def get(self, email: str):
        #TODO: Implementar la lógica para obtener un elemento específico de la lista negra
        return {}, HTTPStatus.OK
