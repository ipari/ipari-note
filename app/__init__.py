from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.config import config
    if not config.is_config_exist():
        config.init_config()

    theme = config.get_config('note')['theme']
    app.static_folder = '../themes/{}/static'.format(theme)
    app.template_folder = '../themes/{}/templates'.format(theme)

    from app.setup import bp as setup_bp
    app.register_blueprint(setup_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.note import bp as note_bp
    app.register_blueprint(note_bp)

    from app.config import bp as config_bp
    app.register_blueprint(config_bp)

    from app.user import bp as user_bp
    app.register_blueprint(user_bp)

    return app
