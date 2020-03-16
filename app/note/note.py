import os
from datetime import datetime
from flask import flash, redirect, render_template, request, send_file, url_for

from app.crypto import decrypt
from app.config.config import get_config, is_file_exist
from app.note.markdown import render_markdown
from app.note.permission import Permission, get_permission
from app.user.user import get_user, is_logged_in


NOTE_EXT = ('.md', '.html')


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


def render_page(file_path, page_path):
    content = render_markdown(file_path)
    meta = get_note_meta()
    menu = get_menu_list()
    return render_template('page.html',
                           meta=meta,
                           menu=menu,
                           pagename=page_path,
                           content=content)


def process_page(page_path, link_verified=False):

    if not link_verified:
        decrypted_page_path = decrypt(page_path)
        if decrypted_page_path is not None:
            permission = get_permission(decrypted_page_path)
            if permission == Permission.LINK_ACCESS:
                return process_page(decrypted_page_path, link_verified=True)

    # 올바른 암호면, 퍼미션을 확인하여 리턴한다.
    permission = get_permission(page_path)

    file_path = get_file_path(page_path)
    if file_path:
        _, ext = os.path.splitext(file_path)
        if ext not in NOTE_EXT:
            # 파일인 경우 URL 직접 접속과 외부 접속을 차단한다.
            if is_logged_in() or (request.referrer and request.url_root in request.referrer):
                return send_file(file_path)
        # 노트는 권한에 따라 다르게 처리한다.
        if is_logged_in()\
                or permission == Permission.PUBLIC\
                or (permission == Permission.LINK_ACCESS and link_verified):
            return render_page(file_path, page_path)

    meta = get_note_meta()
    menu = get_menu_list()

    if is_logged_in():
        message = '문서가 없습니다.'
    else:
        message = '문서가 없거나 권한이 없는 문서입니다.'

    flash(message)
    return render_template('page.html', meta=meta, menu=menu, pagename=page_path)


def get_file_path(page_path):
    base_path = os.path.join(os.getcwd(), 'data/pages', page_path)
    _, ext = os.path.splitext(page_path)

    if ext and is_file_exist(base_path):
        return base_path

    for ext in NOTE_EXT:
        file_path = base_path + ext
        if is_file_exist(file_path):
            return file_path
    return None
