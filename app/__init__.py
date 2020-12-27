from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    from app import user
    app.register_blueprint(user.bp)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app


# def create_app():
#     app = Flask(__name__)
#     app.url_map.strict_slashes = False
#
#     from app.config import config
#     if not config.is_config_exist():
#         config.init_config()
#
#     secret = config.get_config('secret')['key']
#     app.config['SECRET_KEY'] = secret
#
#     theme = config.get_config('note')['theme']
#     app.static_folder = '../themes/{}/static'.format(theme)
#     app.template_folder = '../themes/{}/templates'.format(theme)
#
#     from app.setup import bp as setup_bp
#     app.register_blueprint(setup_bp)
#
#     from app.main import bp as main_bp
#     app.register_blueprint(main_bp)
#
#     from app.note import bp as note_bp
#     app.register_blueprint(note_bp)
#
#     from app.config import bp as config_bp
#     app.register_blueprint(config_bp)
#
#     from app.user import bp as user_bp
#     app.register_blueprint(user_bp)
#
#     return app
