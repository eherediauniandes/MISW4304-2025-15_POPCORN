from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from ..auth import static_bearer_required
from ..extensions import db
from ...models.blacklist import Blacklist
import uuid

class BlacklistCreateResource(Resource):

    @static_bearer_required
    def post(self):
        try:
            # Obtener datos del request
            data = request.get_json()
            
            # Validar que los campos requeridos estén presentes
            if not data:
                return {'error': 'No se proporcionaron datos'}, 400
            
            email = data.get('email')
            app_uuid = data.get('app_uuid')
            blocked_reason = data.get('blocked_reason')
            
            # Validaciones
            if not email:
                return {'error': 'El campo email es requerido'}, 400
            
            if not app_uuid:
                return {'error': 'El campo app_uuid es requerido'}, 400
                
            if not blocked_reason:
                return {'error': 'El campo blocked_reason es requerido'}, 400
            
            # Validar formato UUID
            try:
                uuid.UUID(app_uuid)
            except ValueError:
                return {'error': 'El app_uuid debe ser un UUID válido'}, 400
            
            # Verificar si el email ya existe en la blacklist
            existing_blacklist = Blacklist.query.filter_by(email=email).first()
            if existing_blacklist:
                return {'error': 'El email ya está en la lista negra'}, 409
            
            # Crear nuevo elemento en la blacklist
            new_blacklist = Blacklist(
                email=email,
                app_uuid=app_uuid,
                blocked_reason=blocked_reason
            )
            
            # Guardar en la base de datos
            db.session.add(new_blacklist)
            db.session.commit()
            
            return {
                'message': 'Email agregado a la lista negra exitosamente',
                'data': {
                    'email': new_blacklist.email,
                    'app_uuid': new_blacklist.app_uuid,
                    'blocked_reason': new_blacklist.blocked_reason
                }
            }, 201
            
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Error de integridad en la base de datos'}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f'Error interno del servidor: {str(e)}'}, 500

class BlacklistGetResource(Resource):

    @static_bearer_required
    def get(self, email: str):
        #TODO: Implementar la lógica para obtener un elemento específico de la lista negra
        return {}, 200
