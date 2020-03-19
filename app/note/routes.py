from flask import redirect, request, session, url_for
from app.note import bp
from app.note.note import config_page, process_page
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
