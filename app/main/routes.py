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
    for page_path in iterate_pages():
        permission = permissions.get(page_path, 0)
        if not is_logged_in() and permission != Permission.PUBLIC:
            continue
        page = {
            'title': page_path.split('/')[-1],
            'path': page_path,
            'permission': permission
        }
        file_path = get_md_path(page_path)
        print(os.path.getmtime(file_path))
        _, meta = render_markdown(get_raw_md(file_path))
        page.update(meta)
        pages.append(page)

    pages = sorted(pages, key=lambda x: x['title'])

    base_url = config.get_config('note.base_url')
    menu = get_menu_list()
    meta = get_note_meta()
    meta['logged_in'] = is_logged_in()
    return render_template('archive.html',
                           meta=meta, menu=menu,
                           base_url=base_url, pages=pages)
