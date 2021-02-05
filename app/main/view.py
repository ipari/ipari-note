from flask import Blueprint

bp = Blueprint('main', __name__)


@bp.route('/')
def view_index():
    return 'yay'
