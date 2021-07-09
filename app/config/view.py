from flask import Blueprint


bp = Blueprint('config', __name__)


@bp.route('/config')
def route_config():
    pass
