import os
import yaml
from flask import current_app


def permission_path():
    return os.path.join(current_app.root_path, 'meta', 'permission.yml')


def page_permissions():
    try:
        with open(permission_path(), 'r') as f:
            return yaml.full_load(f) or {}
    except IOError:
        return {}


def page_permission(page_path):
    return page_permissions().get(page_path, 0)


def set_permission(page_path, value):
    permission = int(value)
    if permission > 0:
        permissions = page_permissions()
        permissions[page_path] = permission
        with open(permission_path(), 'w') as f:
            yaml.dump(permissions, f, default_flow_style=False, allow_unicode=True)
    else:
        delete_permission(page_path)


def delete_permission(page_path):
    with open(permission_path(), 'r') as f:
        permissions = yaml.full_load(f) or {}
        try:
            del permissions[page_path]
        except KeyError:
            pass
    with open(permission_path(), 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False, allow_unicode=True)
