import markdown
import os
from flask import Blueprint, request, render_template, send_file

from .config import config, md_extensions
from .cryptography import decrypt, encrypt
from .permission import page_permission, set_permission
from .user import logged_in, user_info


__all__ = ['error_page', 'file_path', 'menu_list', 'note_meta', 'raw_page',
           'render_markdown']


blueprint = Blueprint('note', __name__)


def file_path(page_path):
    base_path = os.path.join('pages', page_path)
    _, file_extension = os.path.splitext(page_path)

    if file_extension:
        return base_path
    return base_path + '.md'


def file_exists(page_path):
    return os.path.isfile(file_path(page_path))


def raw_page(page_path):
    path = file_path(page_path)
    try:
        with open(path, 'r') as f:
            return f.read()
    except IOError:
        return ''


def render_markdown(raw_md):
    extensions = md_extensions()
    return markdown.markdown(raw_md, extensions=extensions)


def render_page(page_path, meta, menu):
    raw_md = raw_page(page_path)
    content = render_markdown(raw_md)
    return render_template('page.html',
                           meta=meta,
                           pagename=page_path,
                           menu=menu,
                           content=content)


def error_page(page_path, meta=None, menu=None, message=''):
    if meta is None:
        meta = note_meta()
    if menu is None:
        menu = menu_list(page_path)
    return render_template('error.html',
                           meta=meta,
                           pagename=page_path,
                           menu=menu,
                           message=message)


def note_meta():
    note_config = config('note')
    meta = dict()
    meta['note_name'] = note_config['name']
    meta['note_description'] = note_config['description']
    meta['user_name'] = user_info('name')
    return meta


def menu_list(page_path=None, file_exists=False):
    items = []
    if logged_in():
        if page_path is not None:
            url = '/edit/{}'.format(page_path)
            if file_exists:
                items.append({'type': 'edit', 'url': url})
            else:
                items.append({'type': 'write', 'url': url})
        items.append({'type': 'archive', 'url': '/archive'})
        items.append({'type': 'config', 'url': '/config'})
        items.append({'type': 'logout', 'url': '/logout'})
    else:
        items.append({'type': 'archive', 'url': '/archive'})
        items.append({'type': 'login', 'url': '/login'})
    return items


def encrypt_url(page_path):
    base_url = config('note')['base_url']
    url = '{}{}/{}'.format(request.url_root, base_url, encrypt(page_path))
    return url


def process_page(page_path, force_allow=False):
    from_link = False
    decrypted_page_path = decrypt(page_path)
    if decrypted_page_path is not None:
        page_path = decrypted_page_path
        from_link = True

    is_file = False
    path, extension = os.path.splitext(page_path)
    if extension:
        if extension == '.md':
            page_path = path
        else:
            is_file = True

    meta = note_meta()
    meta['logged_in'] = logged_in()

    if file_exists(page_path):
        if is_file:
            # 파일인 경우 URL 직접 접속과 외부 접속을 차단한다.
            if logged_in() \
                    or (request.referrer and
                        request.url_root in request.referrer):
                return send_file(file_path(page_path))
        else:
            # 노트인 경우 권한에 따라 다르게 처리한다.
            permission = page_permission(page_path)
            meta['permission'] = permission

            if logged_in() \
                    or permission == 2 \
                    or (force_allow and permission >= 1):

                if permission == 1:
                    # 노트를 공유할 수 있는 암호화된 링크를 보여준다.
                    meta['link'] = encrypt_url(page_path)
                menu = menu_list(page_path=page_path, file_exists=True)
                return render_page(page_path, meta, menu)
            elif from_link and permission == 1:
                return process_page(page_path, force_allow=True)

    # 파일이 없을 때 처리
    menu = menu_list()
    message = "문서가 없거나, 혹은 접근할 권한이 없습니다."

    if logged_in():
        if is_file:
            message = "파일이 없습니다."
        else:
            menu = menu_list(page_path=page_path, file_exists=False)
            message = "문서가 없습니다."

    return error_page(page_path=page_path,
                      meta=meta,
                      menu=menu,
                      message=message)


def config_page(page_path, form):
    if not logged_in():
        message = \
            "페이지 설정 변경에 실패하였습니다."
        return error_page(page_path=page_path,
                          message=message)

    if 'permission' in form:
        permission = int(form['permission'])
        set_permission(page_path, permission)

    return process_page(page_path)


@blueprint.route('/<path:page_path>', methods=['GET', 'POST'])
def view_page(page_path):
    if request.method == 'GET':
        return process_page(page_path)
    else:
        return config_page(page_path, request.form)
