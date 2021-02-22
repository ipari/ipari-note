import os
from flask import Blueprint, request, send_file

from .model import Note
from app.note.note import check_permission, serve_file, serve_page
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
        if note is None:
            note = Note.query.filter_by(encrypted_path=path).first()
        return serve_page(note)
