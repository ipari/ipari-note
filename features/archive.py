import os
from flask import Blueprint, render_template

from .config import config
from .note import menu_list, note_meta, page_permissions
from .user import logged_in


blueprint = Blueprint('archive', __name__)


@blueprint.route('/archive')
def view_archive():
    permissions = page_permissions()
    path = os.path.join('pages')
    pages = []
    for root, subdirs, files in os.walk(path):
        page_dir = '/'.join(root.split('/')[1:])
        for file in files:
            name, ext = os.path.splitext(file)
            if ext != '.md':
                continue
            page_path = os.path.join(page_dir, name)
            permission = permissions.get(page_path, 0)
            if logged_in() or permission == 2:
                pages.append(page_path)

    base_url = config('note')['base_url']
    return render_template('archive.html',
                           meta=note_meta(), menu=menu_list(),
                           base_url=base_url, pages=pages)
