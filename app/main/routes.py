from flask import redirect, url_for

from app.main import bp
from app.config import config
from app.user import user


@bp.route('/')
def route_index():
    main_page = config.get_config('note')['main_page']
    return redirect(url_for('note.route_page', page_path=main_page))


@bp.before_request
def check_setup():
    if config.is_require_setup() or not user.is_user_exists():
        return redirect('/setup/note')
