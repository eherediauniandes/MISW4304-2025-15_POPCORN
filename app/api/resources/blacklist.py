from flask_restful import Resource
from ..auth import static_bearer_required

class BlacklistCreateResource(Resource):

    @static_bearer_required
    def post(self):
        #TODO: Implementar la lógica para crear un nuevo elemento en la lista negra
        return {}, 201

class BlacklistGetResource(Resource):

    @static_bearer_required
    def get(self, email: str):
        #TODO: Implementar la lógica para obtener un elemento específico de la lista negra
        return {}, 200
