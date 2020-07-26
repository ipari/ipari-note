from flask import redirect, url_for

from app.main import bp
from app.user import user
from app.config.config import is_require_setup
from app.note.note import *


@bp.before_request
def check_setup():
    if is_require_setup() or not user.is_user_exists():
        return redirect('/setup/note')


@bp.route('/')
def route_index():
    recent_count = config('note.recent_pages')
    all_pages = get_page_list(sort_key='updated', reverse=True, pinned=True)
    pages = all_pages[:recent_count]
    menu = get_menu_list()
    meta = get_note_meta()
    more_pages = len(all_pages) > recent_count
    return render_template('recent.html',
                           meta=meta, menu=menu,
                           pagename='최근 글', hide_header=True,
                           pages=pages, more_pages=more_pages)


@bp.route('/recent')
def route_recent():
    pages = get_page_list(sort_key='updated', reverse=True, pinned=True)
    menu = get_menu_list()
    meta = get_note_meta()
    base_url = config('note.base_url')
    return render_template('recent.html',
                           meta=meta, menu=menu, base_url=base_url,
                           pagename='모든 글', pages=pages)


@bp.route('/archive')
def route_archive():
    pages = get_page_list(sort_key='updated', reverse=True)
    menu = get_menu_list()
    meta = get_note_meta()
    meta['logged_in'] = is_logged_in()
    return render_template('archive.html',
                           meta=meta, menu=menu, pages=pages)


@bp.route('/tags')
def route_tags():
    tag_infos = get_tag_list()
    menu = get_menu_list()
    meta = get_note_meta()
    return render_template('tags.html',
                           meta=meta, menu=menu, tag_infos=tag_infos)


@bp.route('/tags/<tag>')
def route_tag(tag):
    pages = get_page_list_in_tag(tag)
    menu = get_menu_list()
    meta = get_note_meta()
    return render_template('recent.html',
                           meta=meta, menu=menu,
                           pagename=f'#{tag}', pages=pages)


@bp.route('/update')
def route_update():
    if is_logged_in():
        update_all_page_meta()
        return redirect('/')
    return error_page(page_path=None, message='로그인이 필요합니다.')


@bp.route('/<path:page_path>')
def route_etc(page_path):
    return redirect(url_for('note.route_page', page_path=page_path))
