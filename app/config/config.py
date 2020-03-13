import os
import yaml


CONFIG_FILENAME = 'data/configs/note.yml'
CONFIG_PATH = os.path.join(os.getcwd(), CONFIG_FILENAME)


def get_config(key, default=None):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = yaml.full_load(f)
    except IOError:
        init_config()
        return get_config(key, default=default)
    else:
        return data.get(key, default)


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
