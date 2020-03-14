import os
import yaml
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
