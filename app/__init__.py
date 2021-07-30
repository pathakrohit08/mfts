"""Use this class to create Flask instance.
"""

import os

from celery import Celery
from flask import Blueprint, Flask, render_template, request
from flask_compress import Compress

from config import Config

compress = Compress()


### Instantiate Celery ###
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, result_backend=Config.RESULT_BACKEND)

def create_app():

    app = Flask(__name__)
    compress.init_app(app)
    # Configure the flask app instance
    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(CONFIG_TYPE)

    # Configure celery
    celery.conf.update(app.config) 

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


### Helper Functions ###
def register_blueprints(app):
    from app.documented_endpoints import blueprint as documented_endpoint
    app.register_blueprint(documented_endpoint)


def register_error_handlers(app):
    # 400 - Bad Request
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('400.html',url_index=request.base_url+Config.swagger_url), 400

    # 403 - Forbidden
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html',url_index=request.base_url+Config.swagger_url), 403

    # 404 - Page Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html',url_index=request.base_url+Config.swagger_url), 404

    # 405 - Method Not Allowed
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('405.html',url_index=request.base_url+Config.swagger_url), 405

    # 500 - Internal Server Error
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html',url_index=request.base_url+Config.swagger_url), 500
    
   