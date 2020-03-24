import markdown
from datetime import datetime
from flask import flash, jsonify, render_template, request, send_file, session

from app.crypto import decrypt, encrypt
from app.config.config import get_config, is_file_exist
from app.note.markdown import md_extensions
from app.note.permission import *
from app.user.user import get_user, is_logged_in


NOTE_EXT = ('.md', '.html')
PAGE_ROOT = os.path.join('data', 'pages')


def get_note_meta():
    note_config = get_config('note')
    meta = dict()
    meta['note_title'] = note_config.get('title', '')
    meta['note_subtitle'] = note_config.get('subtitle', '')
    meta['user_name'] = get_user('name')
    meta['year'] = datetime.now().year
    return meta


def get_menu_list(page_path=None, page_exist=False, editable=True):
    items = []
    if is_logged_in():
        if page_path is not None and editable:
            base_url = get_config('note.base_url')
            url = f'/{base_url}/{page_path}/edit'
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


def render_page(file_path, page_path, meta):
    _, ext = os.path.splitext(file_path)
    if ext == '.md':
        content = get_raw_page(file_path)
        content, _ = render_markdown(content)
        menu = get_menu_list(page_path=page_path, page_exist=True)
        return render_template('page.html',
                               meta=meta,
                               menu=menu,
                               pagename=page_path,
                               content=content,
                               html_url=None)
    elif ext == '.html':
        menu = get_menu_list(page_path=page_path, editable=False)
        return render_template('page.html',
                               meta=meta,
                               menu=menu,
                               pagename=page_path,
                               content=None,
                               html_url=page_path + '.html')


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

    _, ext = os.path.splitext(page_path)
    # 파일인 경우 URL 직접 접속과 외부 접속을 차단한다.
    if ext:
        if is_logged_in() or \
                (request.referrer and request.url_root in request.referrer):
            file_path = os.path.join('..', file_path)
            return send_file(file_path)
        return error_page(page_path)
    # 노트는 권한에 따라 다르게 처리한다.
    permission = get_permission(page_path)
    meta = get_note_meta()
    meta['logged_in'] = is_logged_in()
    meta['permission'] = permission
    meta['link'] = encrypt_url(page_path)
    if is_logged_in() or permission == Permission.PUBLIC:
        return render_page(file_path, page_path, meta)
    elif permission == Permission.LINK_ACCESS:
        if decrypt(session.get('key')) == page_path:
            return render_page(file_path, page_path, meta)

    return error_page(page_path)


def config_page(page_path, form):
    if not is_logged_in():
        message = "페이지 설정을 변경하지 못하였습니다."
        return error_page(page_path=page_path, message=message)

    if 'permission' in form:
        permission = int(form['permission'])
        set_permission(page_path, permission)
    return process_page(page_path)


def save_page(page_path, raw_md):
    file_path = get_file_path(page_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(raw_md)


def delete_page(page_path):
    # 퍼미션 제거
    delete_permission(page_path)

    # 파일 제거
    file_path = get_file_path(page_path)
    os.remove(file_path)

    # 빈 디렉터리 제거 (첫 2개는 data/pages)
    page_dir_length = len(PAGE_ROOT.split(os.path.sep))
    dirs = os.path.dirname(file_path).split(os.path.sep)[page_dir_length:]
    for x in range(len(dirs), 0, -1):
        subdir = os.path.join(PAGE_ROOT, *dirs[:x])
        try:
            if len(os.listdir(subdir)) == 0:
                os.rmdir(subdir)
        except OSError:
            continue


def edit_page(page_path):
    file_path = get_file_path(page_path)
    base_url = get_config('note.base_url')
    raw_md = get_raw_page(file_path)
    # ` 문자는 ES6에서 템플릿 문자로 사용되므로 escape 해줘야 한다.
    # https://developer.mozilla.org/ko/docs/Web/JavaScript/Reference/Template_literals
    raw_md = raw_md.replace('`', '\`')
    return render_template('edit.html',
                           pagename=page_path,
                           meta=get_note_meta(),
                           menu=get_menu_list(),
                           base_url=base_url,
                           raw_md=raw_md)


def save_file(page_path, file):
    filename = request.form.get('filename')
    if filename is None:
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f'image-{now}.png'
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = '.png'
        filename += ext
    page_dir = '/'.join(page_path.split('/')[:-1])
    i = 0
    while True:
        if i > 0:
            filename = f'{name}-{i}{ext}'
        file_path = os.path.join(PAGE_ROOT, page_dir, filename)
        if not is_file_exist(file_path):
            break
        i += 1
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    return jsonify(success=True, filename=filename)


def get_file_path(page_path):
    path = os.path.join(PAGE_ROOT, page_path + '.md')
    return os.path.normpath(path)


def find_file_path(page_path):
    base_path = os.path.join(PAGE_ROOT, page_path)
    _, ext = os.path.splitext(page_path)
    if ext and is_file_exist(base_path):
        return os.path.normpath(base_path)
    for ext in NOTE_EXT:
        file_path = base_path + ext
        if is_file_exist(file_path):
            return os.path.normpath(file_path)
    return None


def encrypt_url(page_path):
    url_root = request.url_root
    base_url = get_config('note.base_url')
    url = f'{url_root}{base_url}/{encrypt(page_path)}'
    return url


def get_raw_page(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError:
        return ''


def render_markdown(raw_md):
    extensions = md_extensions()
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(raw_md)
    meta = process_page_meta(md.Meta)
    return html, meta


def process_page_meta(meta):
    for k, v in meta.items():
        v = meta[k][0]
        if k == 'tags':
            v = [tag.strip() for tag in v.split(',')]
        meta[k] = v
    return meta


def iterate_pages(extension=False):
    for root, subdirs, files in os.walk(PAGE_ROOT):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext not in NOTE_EXT:
                continue
            abs_path = os.path.join(root,
                                    file if extension else name)
            page_path = os.path.relpath(abs_path, PAGE_ROOT)
            yield page_path
