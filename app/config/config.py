import os
import yaml
from app.utils import get_value_by_path, set_value_by_path


CONFIG_FILENAME = 'data/configs/note.yml'
CONFIG_PATH = os.path.join(os.getcwd(), CONFIG_FILENAME)


def get_config(path=None, default=None):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = yaml.full_load(f)
    except IOError:
        init_config()
        return get_config(path=path, default=default)
    else:
        if path is None:
            return data
        return get_value_by_path(data, path, default=default)


def set_config(d):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(d, f, default_flow_style=False, allow_unicode=True)


def is_file_exist(path):
    return os.path.isfile(path)


def is_config_exist():
    return is_file_exist(CONFIG_PATH)


def is_require_setup():
    return get_config('require_setup')


def init_config():
    from app.utils import generate_random_string
    config = {
        'note': {
            'base_url': 'note',
            'main_page': 'Home',
            'theme': 'yaong',
        },
        'markdown_extensions': {
            'toc_marker': '[목차]',
        },
        'secret': {
            'key': generate_random_string()
        },
        'require_setup': True
    }
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
