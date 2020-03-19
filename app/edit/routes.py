import re
from flask import redirect, request, url_for
from app.edit import bp
from app.edit.edit import delete_page, edit_page, save_page
from app.utils import config
from app.note.note import error_page, is_logged_in, render_markdown


@bp.route('/preview', methods=['POST'])
def preview():
    if request.method == 'POST':
        html = render_markdown(request.get_json()['raw_md'])

        # 이미지 주소가 /edit 기준으로 렌더링되어있어 base_url 기준으로 고친다.
        page_root = request.referrer.split('/')[-2]
        base_url = config('note.base_url')
        rel_url = '{}/{}'.format(base_url, page_root)

        def replace_path(matchobj):
            return '{}/{}/{}{}'.format(matchobj.group(1), rel_url,
                                       matchobj.group(2), matchobj.group(3))

        pattern = r'(src=\")([^\"]*)(\")'
        html = re.sub(pattern, replace_path, html)
        return html


@bp.route('/edit/<path:page_path>', methods=['GET', 'POST'])
def route_edit(page_path):
    if not is_logged_in():
        message = "로그인 후에 편집할 수 있습니다."
        return error_page(page_path=page_path, message=message)

    if request.method == 'GET':
        return edit_page(page_path)
    elif request.method == 'POST':
        raw_md = request.form['md']
        if raw_md:
            save_page(page_path, raw_md)
        else:
            delete_page(page_path)
        return redirect(url_for('note.route_page', page_path=page_path))
