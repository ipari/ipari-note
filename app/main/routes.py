from flask import redirect

from app.main import bp
from app.config import config
from app.user import user


@bp.route('/')
def index():
    return 'Hello, ipari.'


@bp.before_request
def check_setup():
    if config.is_require_setup() or not user.is_user_exists():
        return redirect('/setup/note')
