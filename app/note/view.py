import os
from flask import Blueprint, url_for, redirect, request, send_file

from .model import Note
from app.user.user import is_logged_in
from app.note.note import *
from app.main.view import get_post_info_from_notes
from app.utils import config


url_prefix = config('note')['base_url']
bp = Blueprint('note', __name__, url_prefix=f'/{url_prefix}')


@bp.route('/')
def route_note():
    if is_logged_in():
        notes = Note.query.order_by(Note.updated.desc()).all()
    else:
        notes = Note.query.filter_by(permission=Permission.PUBLIC)\
            .order_by(Note.updated.desc())\
            .all()

    pages = get_post_info_from_notes(notes)
    menu = get_menu_list()
    meta = get_base_meta()
    meta['logged_in'] = is_logged_in()
    return render_template('pages.html',
                           meta=meta, menu=menu,
                           pagename='목록', pages=pages)


@bp.route('/<path:page_path>', methods=['GET', 'POST'])
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
    if not is_logged_in():
        message = "로그인 후에 편집할 수 있습니다."
        return error_page(page_path=page_path, message=message)

    if request.method == 'GET':
        return edit_page(page_path)
    elif request.method == 'POST':
        update_page(page_path, request.form['md'])
        return redirect(url_for('note.route_page', page_path=page_path))
