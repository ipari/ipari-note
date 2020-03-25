from flask import redirect

from app.main import bp
from app.config import config
from app.user import user
from app.note.note import *


@bp.before_request
def check_setup():
    if config.is_require_setup() or not user.is_user_exists():
        return redirect('/setup/note')


@bp.route('/')
def route_index():
    recent_count = config.get_config('note.recent_pages')
    all_pages = get_page_list(sort_key='updated', reverse=True)
    pages = all_pages[:recent_count]
    menu = get_menu_list()
    meta = get_note_meta()
    base_url = config.get_config('note.base_url')
    more_pages = len(all_pages) > recent_count
    return render_template('recent.html',
                           meta=meta, menu=menu,
                           base_url=base_url, pages=pages,
                           more_pages=more_pages)


@bp.route('/recent')
def route_recent():
    update_all_page_meta()
    pages = get_page_list(sort_key='updated', reverse=True)
    menu = get_menu_list()
    meta = get_note_meta()
    base_url = config.get_config('note.base_url')
    return render_template('recent.html',
                           meta=meta, menu=menu,
                           base_url=base_url, pages=pages)


@bp.route('/archive')
def view_archive():
    update_all_page_meta()
    pages = get_page_list(sort_key='path')
    base_url = config.get_config('note.base_url')
    menu = get_menu_list()
    meta = get_note_meta()
    meta['logged_in'] = is_logged_in()
    return render_template('archive.html',
                           meta=meta, menu=menu,
                           base_url=base_url, pages=pages)
