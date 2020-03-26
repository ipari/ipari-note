import os
import yaml
from enum import IntEnum
from app.utils import dump_yaml


PERMISSION_FILENAME = 'data/configs/permission.yml'
PERMISSION_PATH = os.path.join(os.getcwd(), PERMISSION_FILENAME)


class Permission(IntEnum):
    PRIVATE = 0
    LINK_ACCESS = 1
    PUBLIC = 2


def get_permission(page_path=None):
    try:
        with open(PERMISSION_PATH, 'r', encoding='utf-8') as f:
            data = yaml.full_load(f)
    except IOError:
        data = {}
    if page_path is None:
        return data
    return data.get(page_path, Permission.PRIVATE)


def set_permission(page_path, permission):
    permissions = get_permission()
    if permission == Permission.PRIVATE:
        if page_path in permissions:
            del permissions[page_path]
    else:
        permissions[page_path] = permission
    dump_yaml(permissions, PERMISSION_PATH)


def delete_permission(page_path):
    set_permission(page_path, Permission.PRIVATE)
