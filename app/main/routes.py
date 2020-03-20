import os
from flask import redirect, url_for

from app.main import bp
from app.config import config
from app.user import user
from app.note.note import *
from app.note.permission import get_permission


@bp.route('/')
def route_index():
    main_page = config.get_config('note')['main_page']
    return redirect(url_for('note.route_page', page_path=main_page))


@bp.before_request
def check_setup():
    if config.is_require_setup() or not user.is_user_exists():
        return redirect('/setup/note')


@bp.route('/archive')
def view_archive():
    permissions = get_permission()
    pages = []
    for root, subdirs, files in os.walk(PAGE_ROOT):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext not in NOTE_EXT:
                continue
            abs_path = os.path.join(root, name)
            page_path = os.path.relpath(abs_path, PAGE_ROOT)
            permission = permissions.get(page_path, 0)
            if is_logged_in() or permission == Permission.PUBLIC:
                pages.append(page_path)

    base_url = config.get_config('note.base_url')
    pages = sorted(pages)
    meta = get_note_meta()
    menu = get_menu_list()
    return render_template('archive.html',
                           meta=meta, menu=menu,
                           base_url=base_url, pages=pages)
