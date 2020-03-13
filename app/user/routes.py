from app.user import bp


@bp.route('/user')
def route_user():
    return f'User page.'
