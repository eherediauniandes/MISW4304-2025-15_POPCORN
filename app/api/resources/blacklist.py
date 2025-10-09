from flask_restful import Resource

class BlacklistCreateResource(Resource):

    def post(self):
        #TODO: Implementar la lógica para crear un nuevo elemento en la lista negra
        return {}, 201

class BlacklistGetResource(Resource):
    def get(self, email: str):
        #TODO: Implementar la lógica para obtener un elemento específico de la lista negra
        return {}, 200
