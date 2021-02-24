import os
from flask import Blueprint, request, send_file

from .model import Note
from app.user.user import is_logged_in
from app.note.note import *
from app.utils import config


url_prefix = config('note')['base_url']
bp = Blueprint('note', __name__, url_prefix=f'/{url_prefix}')


@bp.route('/')
def route_note():
    return 'redirect to main page'


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
        return "404 Not Found"


@bp.route('/<path:page_path>/edit', methods=['GET', 'POST'])
def route_edit(page_path):
    if not is_logged_in():
        message = "로그인 후에 편집할 수 있습니다."
        return message

    if request.method == 'GET':
        return "edit"
    elif request.method == 'POST':
        return "edited"
