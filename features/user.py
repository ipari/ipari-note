import os
import yaml
from flask import Blueprint, current_app, request, redirect, render_template, url_for

from .cryptography import compare_hash_with_text
from .note import note_meta
from .config import config


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


@blueprint.route('/login', methods=['GET', 'POST'])
def view_login():
    if request.method == 'GET':
        meta = note_meta()
        return render_template('login.html', meta=meta)

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
        # TODO: 로그인 처리

        # 리다이렉트
        if form_referrer:
            return redirect(form_referrer)

        main_page = config('note')['main_page']
        return redirect(url_for('note.view_page', page_path=main_page))

    # TODO: 로그인 실패 페이지
    meta = note_meta()
    form = {
        'email': form_email,
        'referrer': form_referrer
    }
    return render_template('login.html', meta=meta, form=form)
