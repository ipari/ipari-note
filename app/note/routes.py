import os
from flask import request, send_file
from app.config import config
from app.note import bp
from app.note.note import process_page
from app.user import user


@bp.route('/<path:page_path>', methods=['GET', 'POST'])
def route_page(page_path):
    if request.method == 'GET':
        return process_page(page_path)
    return f'config page: {page_path}'
