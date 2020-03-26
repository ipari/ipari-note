import copy
import operator
import os
import random
import string
import yaml
from functools import reduce


def config(path=None, default=None):
    from app.config.config import get_config
    return get_config(path=path, default=default)


def get_value_by_path(d, path, reduce_func=reduce, default=None):
    """nest dict 의 값을 str 로 지정된 키로 가져온다.

    >> d = {'a': {'aa': {'aaa': 1, 'aab': 2}}}
    >> get_value_by_path(d, 'a.aa')
    >> {'aaa': 1, 'aab': 2}

    Args:
        d: dict
        path: 'a.aa' or ['a', 'aa']
        reduce_func: reduce 에 사용할 함수. set_value_by_path 때문에 존재.
        default: KeyError 발생 시 리턴값

    Returns:
    """
    if isinstance(path, str):
        path = path.split('.')
    try:
        return reduce_func(operator.getitem, path, d)
    except KeyError:
        return default


def set_value_by_path(d, path, value):
    """nest dict 에서 str 로 지정된 키의 값을 수정한다.

    >> d = {'a': {'aa': {'aaa': 1, 'aab': 2}}}
    >> set_value_by_path(d, 'a.aa', {'aaa': 3, 'xxx': 1})
    >> {'a': {'aa': {'aaa': 3, 'aab': 2, 'xxx': 1}}}

    Args:
        d: dict
        path: 'a.aa', ['a', 'aa']
        value: path 에 새로 지정할 값
    Returns: dict
    """
    def custom_reduce(function, iterable, initializer):
        """reduce 에서 없는 키에 접근하면 새로 생성하도록 한다."""
        it = iter(iterable)
        v = initializer
        for element in it:
            try:
                v = function(v, element)
            except KeyError:
                v[element] = dict()
                v = v[element]
        return v

    if isinstance(path, str):
        path = path.split('.')

    new_d = copy.deepcopy(d)
    target = get_value_by_path(new_d, path[:-1], reduce_func=custom_reduce)
    key = path[-1]
    if isinstance(target[key], dict) and isinstance(value, dict):
        target[key].update(value)
    else:
        target[key] = value

    return new_d


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
