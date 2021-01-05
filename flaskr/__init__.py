from flask import Flask
from importlib import import_module
from ymm import Configuration, Controller, MusicBulb

config = Configuration()
controller = Controller(config)


def register_blueprints(app):
    for module_name in ('base', 'home'):
        module = import_module('flaskr.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def create_app(cfg):
    app = Flask(__name__, static_folder='base/static')
    app.config.from_object(cfg)
    register_blueprints(app)
    return app
