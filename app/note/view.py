import re
import time
from flask import Blueprint, redirect, request

from app.note.note import *


# FIXME: 수정해야함
url_prefix = 'note'
bp = Blueprint('note', __name__, url_prefix=f'/{url_prefix}')


@bp.route('/')
def route_note():
    if User.is_logged_in():
        notes = Note.query.order_by(Note.updated.desc()).all()
    else:
        notes = Note.query.filter_by(permission=Permission.PUBLIC)\
            .order_by(Note.updated.desc())\
            .all()

    pages = get_post_info_from_notes(notes)
    menu = get_menu_list()
    meta = get_base_meta()
    meta['logged_in'] = User.is_logged_in()
    return render_template('pages.html',
                           meta=meta, menu=menu,
                           pagename='목록', pages=pages)


@bp.route('/<path:page_path>', methods=['GET', 'POST'], strict_slashes=False)
def route_page(page_path):
    if request.method == 'GET':
        path, ext = os.path.splitext(page_path)
        if ext:
            return serve_file(page_path)

        note = Note.query.filter_by(path=path).first()
        if note:
            return serve_page(note)
        note = Note.query.filter_by(encrypted_path=path).first()
        if note:
            return serve_page(note, from_encrypted_path=True)
        return error_page(page_path)


@bp.route('/<path:page_path>/edit', methods=['GET', 'POST'])
def route_edit(page_path):
    if not User.is_logged_in():
        message = "로그인 후에 편집할 수 있습니다."
        return error_page(page_path=page_path, message=message)

    if request.method == 'GET':
        return edit_page(page_path)
    elif request.method == 'POST':
        update_page(page_path, request.form['md'])
        time.sleep(0.5)
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
