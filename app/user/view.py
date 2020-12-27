from flask import Blueprint, request, session
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField

from app import db
from app.user.model import User


bp = Blueprint('user', __name__)


class LoginForm(FlaskForm):
    referrer = HiddenField()
    email = StringField('이메일')
    password = PasswordField('비밀번호')
    submit = SubmitField('로그인')


@bp.route('/add')
def user_add():
    user = User(
        email='me@ipari.dev',
        password='282',
        name='이파리',
    )
    db.session.add(user)
    db.session.commit()
    return 'User added'


@bp.route('/view')
def user_view():
    user = User.get_by_session()
    if user is None:
        return 'No user exists'
    return repr(user)


@bp.route('/login', methods=['GET'])
def user_login():
    email = request.args.get('email', '')
    user = User.query.filter_by(email=email).first()
    if user is None:
        return 'Invalid User'

    session['email'] = email
    return 'Login success'


@bp.route('/logout')
def user_logout():
    User.logout()
    return 'Logout success'
