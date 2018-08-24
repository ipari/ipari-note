import os
import re
from flask import Blueprint, redirect, request, render_template, url_for

from .config import config
from .note import *
from .permission import delete_permission
from .user import logged_in


blueprint = Blueprint('edit', __name__)


def save_note(page_path, content):
    path = file_path(page_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)


def edit_page(page_path):
    base_url = config('note')['base_url']
    content = raw_page(page_path)
    # ` 문자는 ES6에서 템플릿 문자로 사용되므로 escape 해줘야 한다.
    content = content.replace('`', '\`')
    return render_template('edit.html',
                           pagename=page_path,
                           meta=note_meta(),
                           base_url=base_url,
                           menu=menu_list(),
                           content=content)


def delete_page(page_path):
    # 퍼미션 제거
    delete_permission(page_path)

    # 노트 제거
    path = file_path(page_path)
    os.remove(path)

    # 빈 디렉터리 제거
    dirs = os.path.dirname(path).split('/')
    for x in range(len(dirs), 0, -1):
        subdir = os.path.join(*dirs[:x])
        try:
            os.rmdir(subdir)
        except OSError:
            continue


@blueprint.route('/preview', methods=['POST'])
def preview():
    html = render_markdown(request.get_json()['raw_md'])

    # 이미지 주소가 /edit 기준으로 렌더링되어있어 base_url 기준으로 고친다.
    page_root = request.referrer.split('/')[-2]
    base_url = config('note')['base_url']
    rel_url = '{}/{}'.format(base_url, page_root)

    def replace_path(matchobj):
        return '{}/{}/{}{}'.format(matchobj.group(1), rel_url,
                                   matchobj.group(2), matchobj.group(3))

    pattern = r'(src=\")([^\"]*)(\")'
    html = re.sub(pattern, replace_path, html)
    return html


@blueprint.route('/edit/<path:page_path>', methods=['GET', 'POST'])
def view_edit(page_path):
    if not logged_in():
        message = "로그인 후에 편집할 수 있습니다."
        return error_page(page_path=page_path,
                          message=message)
    else:
        if request.method == 'GET':
            return edit_page(page_path)
        else:
            raw_md = request.form['md']
            if raw_md:
                save_note(page_path, request.form['md'])
            else:
                delete_page(page_path)
            return redirect(url_for('note.view_page', page_path=page_path))
