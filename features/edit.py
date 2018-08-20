import re
from flask import Blueprint, redirect, request, render_template

from .config import config
from .note import file_path, menu_list, note_meta, process_page, raw_page, \
    render_markdown
from .user import logged_in


blueprint = Blueprint('edit', __name__)


def save_note(page_path, content):
    path = file_path(page_path)
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
        return redirect('/login')
    else:
        if request.method == 'GET':
            return edit_page(page_path)
        else:
            save_note(page_path, request.form['md'])
            return process_page(page_path)
