from flask import render_template
from app.user import bp


@bp.route('/user')
def route_user():
    return render_template('user.html')
