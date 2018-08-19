import os
import yaml
from flask import Blueprint, current_app, request, redirect, render_template,\
    session

from .cryptography import compare_hash_with_text
from .note import menu_list, note_meta


blueprint = Blueprint('user', __name__)


def user_info_path():
    return os.path.join(current_app.root_path, 'meta', 'user.yml')


def user_info(key):
    try:
        with open(user_info_path(), 'r') as f:
            data = yaml.load(f)
    except IOError:
        print('no user info in {}'.format(user_info_path()))
    else:
        if key is None:
            return data
        return data.get(key, None)


def logged_in():
    return 'user' in session


@blueprint.route('/login', methods=['GET', 'POST'])
def view_login():
    menu = menu_list()
    if request.method == 'GET':
        if logged_in():
            return redirect('/')
        form = {'referrer': request.referrer}
        return render_template('login.html',
                               meta=note_meta(), menu=menu, form=form)

    user_email = user_info('email')
    user_password = user_info('password')

    form_email = request.form['email']
    form_password = request.form['password']
    form_referrer = request.form['referrer']

    if not user_password:
        # TODO: 비밀번호 초기화 페이지
        return '비밀번호 초기화 하시는군여?'

    email_valid = user_email == form_email
    password_valid = compare_hash_with_text(user_password, form_password)

    if email_valid and password_valid:
        session['user'] = user_email

        # 리다이렉트
        if form_referrer:
            return redirect(form_referrer)
        return redirect('/')

    form = {
        'email': form_email,
        'referrer': form_referrer,
        'error': True
    }
    return render_template('login.html',
                           meta=note_meta(), menu=menu, form=form)


@blueprint.route('/logout')
def view_logout():
    session.pop('user', None)
    if request.referrer is None:
        return redirect('/login')
    return redirect(request.referrer)
