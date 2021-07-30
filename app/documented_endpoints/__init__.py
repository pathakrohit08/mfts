from flask import Blueprint
from flask_restx import Api

#from blueprints.documented_endpoints.entities import namespace as entities_ns
from app.documented_endpoints.resources import namespace as resource_ns

blueprint = Blueprint('swagger', __name__, url_prefix='/swagger')

api_extension = Api(
    blueprint,
    title='Money flow trader system API Documentation',
    version='v1.0',
    contact_email='',
    description='Money flow trading system automated api',
    doc='/ui/index'
)

#api_extension.add_namespace(entities_ns)
api_extension.add_namespace(resource_ns)
