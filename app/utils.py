import os
import random
import string
import yaml


def generate_random_string(length=32):
    letters = string.ascii_letters + string.digits
    text = ''.join(random.choice(letters) for _ in range(length))
    return text


def dump_yaml(data, path):
    path = os.path.normpath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        # https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
        yaml.Dumper.ignore_aliases = lambda *args: True
        yaml.safe_dump(data, f,  default_flow_style=False, allow_unicode=True)


def is_file_exist(path):
    return os.path.isfile(path)


def load_yaml(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return None


def format_datetime(dt, style=None, timezone=None):
    if style == 'iso-8601':
        dt_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
        if timezone:
            dt_str += timezone
        return dt_str
    elif style == 'rfc-822':
        dt_str = dt.strftime('%a, %d %b %Y %H:%M:%S')
        if timezone:
            dt_str += f' {timezone.replace(":", "")}'
        return dt_str
    else:
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dt_str
