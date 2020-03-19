import markdown
import os
from datetime import datetime
from flask import flash, render_template, request, send_file, session

from app.crypto import decrypt, encrypt
from app.config.config import get_config, is_file_exist
from app.note.markdown import md_extensions
from app.note.permission import Permission, get_permission, set_permission
from app.user.user import get_user, is_logged_in


NOTE_EXT = ('.md', '.html')
PAGE_DIR = 'data/pages'


def get_note_meta():
    note_config = get_config('note')
    meta = dict()
    meta['note_title'] = note_config.get('title', '')
    meta['note_subtitle'] = note_config.get('subtitle', '')
    meta['user_name'] = get_user('name')
    meta['year'] = datetime.now().year
    return meta


def get_menu_list(page_path=None, page_exist=False):
    items = []
    if is_logged_in():
        if page_path is not None:
            url = '/edit/{}'.format(page_path)
            if page_exist:
                items.append({'type': 'edit', 'url': url, 'label': '편집'})
            else:
                items.append({'type': 'write', 'url': url, 'label': '작성'})
        items.append({'type': 'archive', 'url': '/archive', 'label': '목록'})
        items.append({'type': 'config', 'url': '/config', 'label': '설정'})
        items.append({'type': 'logout', 'url': '/logout', 'label': '로그아웃'})
    else:
        items.append({'type': 'archive', 'url': '/archive', 'label': '목록'})
        items.append({'type': 'login', 'url': '/login', 'label': '로그인'})
    return items


def render_page(file_path, page_path, meta, menu):
    content = render_markdown(file_path)
    return render_template('page.html',
                           meta=meta,
                           menu=menu,
                           pagename=page_path,
                           content=content)


def error_page(page_path, message=None):
    meta = get_note_meta()
    menu = get_menu_list(page_path=page_path)
    if message is None:
        if is_logged_in():
            message = '문서가 없습니다.'
        else:
            message = '문서가 없거나 권한이 없는 문서입니다.'
    flash(message)
    return render_template('page.html', meta=meta, menu=menu, pagename=page_path)


def process_page(page_path):
    file_path = find_file_path(page_path)
    if not file_path:
        return error_page(page_path)

    _, ext = os.path.splitext(file_path)
    # 파일인 경우 URL 직접 접속과 외부 접속을 차단한다.
    if ext not in NOTE_EXT:
        if is_logged_in() or (request.referrer and request.url_root in request.referrer):
            return send_file(file_path)
        return error_page(page_path)
    # 노트는 권한에 따라 다르게 처리한다.
    permission = get_permission(page_path)
    menu = get_menu_list(page_path=page_path, page_exist=True)
    meta = get_note_meta()
    meta['logged_in'] = is_logged_in()
    meta['permission'] = permission
    meta['link'] = encrypt_url(page_path)
    if is_logged_in() or permission == Permission.PUBLIC:
        return render_page(file_path, page_path, meta, menu)
    elif permission == Permission.LINK_ACCESS:
        if decrypt(session.get('key')) == page_path:
            return render_page(file_path, page_path, meta, menu)

    return error_page(page_path)


def config_page(page_path, form):
    if not is_logged_in():
        message = "페이지 설정을 변경하지 못하였습니다."
        return error_page(page_path=page_path, message=message)

    if 'permission' in form:
        permission = int(form['permission'])
        set_permission(page_path, permission)
    return process_page(page_path)


def get_file_path(page_path):
    return os.path.join(PAGE_DIR, page_path + '.md')


def find_file_path(page_path):
    base_path = os.path.join(PAGE_DIR, page_path)
    _, ext = os.path.splitext(page_path)

    if ext and is_file_exist(base_path):
        return base_path

    for ext in NOTE_EXT:
        file_path = base_path + ext
        if is_file_exist(file_path):
            return file_path
    return None


def encrypt_url(page_path):
    url_root = request.url_root
    base_url = get_config('note.base_url')
    url = f'{url_root}{base_url}/{encrypt(page_path)}'
    return url


def get_raw_page(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except IOError:
        return ''


def render_markdown(file_path):
    extensions = md_extensions()
    raw_md = get_raw_page(file_path)
    return markdown.markdown(raw_md, extensions=extensions)