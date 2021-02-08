import os
from flask import Blueprint, request, send_file

from .model import Note
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
            return send_file(path)

        note = Note.query.filter_by(path=path).first()
        # TODO: Check permission and login status
        if note:
            # return render_template()
            return f'serve page: {path}'

        note = Note.query.filter_by(encrypted_path=path).first()
        # TODO: Check permission and login status
        if note:
            # return render_template()
            return f'serve page: {note.encrypted_path}'

        return '404 Not Found'
