from app.setup import bp
from flask import render_template


@bp.route('/note')
def route_setup_note():
    return render_template('setup/note.html')


@bp.route('/user')
def route_setup_user():
    return render_template('setup/user.html')
