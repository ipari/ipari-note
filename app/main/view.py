from flask import Blueprint

from app.note.note import update_all


bp = Blueprint('main', __name__)


@bp.route('/')
def view_index():
    return 'yay'


@bp.route('/update')
def view_update():
    update_all()
    return 'update'
