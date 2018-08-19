import markdown
import os
import yaml
from flask import Blueprint, current_app, request, render_template, send_file

from features.config import config, md_extensions
from features.cryptography import decrypt
from .user import logged_in


blueprint = Blueprint('note', __name__)


def file_path(page_path):
    base_path = os.path.join(current_app.root_path, 'pages', page_path)
    _, file_extension = os.path.splitext(page_path)

    if file_extension:
        return base_path
    return base_path + '.md'


def file_exists(page_path):
    return os.path.isfile(file_path(page_path))


def page_permission(page_path):
    path = os.path.join(current_app.root_path, 'meta', 'permission.yml')
    try:
        with open(path, 'r') as f:
            permission = yaml.load(f)
            return permission.get(page_path, 0)
    except IOError:
        return 0


def render_page(page_path, menu):
    path = file_path(page_path)

    with open(path, 'r') as f:
        extensions = md_extensions()
        content = markdown.markdown(f.read(), extensions=extensions)
        meta = note_meta()
        return render_template('page.html',
                               meta=meta,
                               pagename=page_path,
                               menu=menu,
                               content=content)


def note_meta():
    note_config = config('note')
    meta = dict()
    meta['note_name'] = note_config['name']
    meta['note_description'] = note_config['description']
    return meta


def menu_list(page_path=None, file_exists=False):
    items = []
    if logged_in():
        items.append({'type': 'logout', 'url': '/logout'})
        if page_path is not None:
            url = '/edit/{}'.format(page_path)
            if file_exists:
                items.append({'type': 'edit', 'url': url})
            else:
                items.append({'type': 'write', 'url': url})
        items.append({'type': 'archive', 'url': '/archive'})
        items.append({'type': 'config', 'url': '/config'})
    else:
        items.append({'type': 'login', 'url': '/login'})
        items.append({'type': 'archive', 'url': '/archive'})
    return items


@blueprint.route('/<path:page_path>')
def view_page(page_path, force_allow=False):
    from_link = False
    decrypted_page_path = decrypt(page_path)
    if decrypted_page_path is not None:
        page_path = decrypted_page_path
        from_link = True

    _, file_extension = os.path.splitext(page_path)
    # .md 로 접근하면 페이지를 렌더링한다.
    if file_extension == '.md':
        page_path = page_path[:-3]
        file_extension = None

    permission = page_permission(page_path)
    if file_exists(page_path):
        if file_extension:
            # 파일인 경우 URL 직접 접속과 외부 접속을 차단한다.
            if logged_in() \
                    or (request.referrer and
                        request.url_root in request.referrer):
                return send_file(file_path(page_path))
        else:
            if logged_in() \
                    or permission == 2 \
                    or (force_allow and permission >= 1):
                menu = menu_list(page_path=page_path, file_exists=True)
                return render_page(page_path, menu)
            elif from_link and permission == 1:
                return view_page(page_path, force_allow=True)
            else:
                # TODO: 로그인 중이면 새 페이지 만들기로 보낸다.
                pass

    # TODO: 에러 페이지를 제대로 만들자...
    return "문서가 없거나, 혹은 접근할 권한이 없습니다."
