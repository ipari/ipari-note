import re
from flask import redirect, url_for
from app.note import bp
from app.note.note import *
from app.crypto import decrypt


@bp.route('/<path:page_path>', methods=['GET', 'POST'])
def route_page(page_path):
    if request.method == 'GET':
        decrypted_page_path = decrypt(page_path)
        if decrypted_page_path:
            session['key'] = page_path
            return redirect(
                url_for('note.route_page', page_path=decrypted_page_path)
            )
        return process_page(page_path)
    if request.method == 'POST':
        return config_page(page_path, request.form)


@bp.route('/preview', methods=['POST'])
def preview():
    if request.method == 'POST':
        html, _ = render_markdown(request.get_json()['raw_md'])

        # ipari-note/guide 는 ipari-note 폴더의 guide.md 파일을 보여준다.
        # 그러므로 각종 경로에 ../ 를 붙여 한 단계 위에서 파일을 찾도록 한다.
        def replace_path(matchobj):
            return '{}{}/{}{}'.format(matchobj.group(1), '..',
                                      matchobj.group(2), matchobj.group(3))
        pattern = r'(src=\")([^\"]*)(\")'
        html = re.sub(pattern, replace_path, html)
        return html


@bp.route('/<path:page_path>/edit', methods=['GET', 'POST'])
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


@bp.route('/<path:page_path>/upload', methods=['POST'])
def route_upload(page_path):
    if request.method == 'POST':
        if 'file' not in request.files:
            # no file part
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            # no selected file
            return redirect(request.url)
        if file:
            return save_file(page_path, file)
