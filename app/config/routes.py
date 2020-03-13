from app.config import bp


@bp.route('/config')
def route_config():
    return 'Config page'
