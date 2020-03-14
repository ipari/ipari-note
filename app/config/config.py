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


def set_config(path, value):
    config = get_config(path, value)
    config = set_value_by_path(config, path, value)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f)


def is_config_exist():
    return os.path.isfile(CONFIG_PATH)


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
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
