import os
import yaml
from flask import session
from werkzeug.security import check_password_hash
from app.utils import get_value_by_path


USER_FILENAME = 'data/configs/user.yml'
USER_PATH = os.path.join(os.getcwd(), USER_FILENAME)


def get_user(path=None):
    try:
        with open(USER_PATH, 'r', encoding='utf-8') as f:
            data = yaml.full_load(f)
    except IOError:
        pass
    else:
        if path is None:
            return data
        return get_value_by_path(data, path)


def set_user(d):
    with open(USER_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(d, f, default_flow_style=False, allow_unicode=True)


def is_user_exists():
    return os.path.isfile(USER_PATH)


def is_logged_in():
    return 'user' in session


def log_in(form):
    user = get_user()
    is_valid_email = user['email'] == form.email.data
    is_valid_password = check_password_hash(user['password'], form.password.data)
    if is_valid_email and is_valid_password:
        session['user'] = user['email']
        return True
