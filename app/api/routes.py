from flask_restful import Api
from .resources.blacklist import BlacklistCreateResource, BlacklistGetResource

def register_resources(api: Api) -> None:
    api.add_resource(BlacklistCreateResource, "/blacklists")
    api.add_resource(BlacklistGetResource, "/blacklists/<string:email>")
