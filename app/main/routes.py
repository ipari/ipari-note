from flask import g, redirect, current_app

from app.main import bp
from app.config import config


@bp.route('/')
def index():
    return 'Hello, ipari.'


@bp.before_request
def check_setup():
    if config.is_require_setup():
        return redirect('/setup/note')
