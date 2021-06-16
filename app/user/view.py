from flask import Blueprint, flash, redirect, request, render_template, session
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField

from app import db
from app.note.note import get_base_meta, get_menu_list
from app.user.model import User
from app.user.user import is_logged_in, log_in


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


@bp.route('/login', methods=['GET', 'POST'])
def route_login():
    if is_logged_in():
        return redirect('/')

    form = LoginForm()
    if request.method == 'GET':
        form.referrer.data = request.referrer
        meta = get_base_meta()
        menu = get_menu_list()
        return render_template('login.html', form=form, meta=meta, menu=menu,
                               pagename='로그인')

    if log_in(form):
        if form.referrer:
            return redirect(form.referrer.data)
        return redirect('/')

    flash('입력한 값이 맞는지 확인해주세요.')
    return redirect('/login')


@bp.route('/logout')
def user_logout():
    User.logout()
    return 'Logout success'
