import os

from flask import Flask
from flask_bootstrap import Bootstrap

from .config import config

bootstrap = Bootstrap()


def getenv(key: str) -> str:
    return os.getenv(key)


def get_field_value(field):
    return field.data


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flask_learn.db'),
    # )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app_env = (app.config['ENV']
                   if app.config['ENV'] in config else 'default')
        app.config.from_object(config[app_env])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    bootstrap.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import electronics, views
    app.add_template_filter(getenv)
    app.add_template_filter(get_field_value)
    app.register_blueprint(views.bp)
    app.register_blueprint(electronics.bp)
    app.add_url_rule('/', endpoint='index')

    return app
