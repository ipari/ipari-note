import os
from flask import Blueprint, current_app, render_template

from .config import config
from .note import menu_list, note_meta
from .permission import page_permissions
from .user import logged_in


blueprint = Blueprint('archive', __name__)


@blueprint.route('/archive')
def view_archive():
    permissions = page_permissions()
    page_root = os.path.join(current_app.root_path, 'pages')
    pages = []
    for root, subdirs, files in os.walk(page_root):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext != '.md':
                continue
            abs_path = os.path.join(root, name)
            page_path = os.path.relpath(abs_path, page_root)
            permission = permissions.get(page_path, 0)
            if logged_in() or permission == 2:
                pages.append(page_path)

    base_url = config('note')['base_url']
    pages = sorted(pages)
    return render_template('archive.html',
                           meta=note_meta(), menu=menu_list(),
                           base_url=base_url, pages=pages)
