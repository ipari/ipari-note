import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(instance_path=None):
    app = Flask(__name__, instance_path=instance_path)

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    app.config.from_pyfile('../config.py')

    from app import main, user, note, config
    app.register_blueprint(main.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(note.bp)
    app.register_blueprint(config.bp)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        from app.config.model import Config
        from app.user.model import User
        Config.update_config()
        User.update_user()

    # FIXME: 설정에서 가져오도록
    theme = 'yaong'
    app.static_folder = '../themes/{}/static'.format(theme)
    app.template_folder = '../themes/{}/templates'.format(theme)

    return app
