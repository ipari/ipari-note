import markdown
import os
from flask import Blueprint, current_app, render_template, send_file

from features.config import config, md_extensions


blueprint = Blueprint('note', __name__)


@blueprint.route('/<path:page_path>')
def view_page(page_path):
    base_path = os.path.join(current_app.root_path, 'pages', page_path)
    _, file_extension = os.path.splitext(page_path)

    if file_extension and file_extension != '.md':
        return send_file(base_path)

    data_path = base_path + '.md'
    with open(data_path, 'r') as f:
        extensions = md_extensions()
        note_name = config('note')['name']
        note_description = config('note')['description']
        content = markdown.markdown(f.read(), extensions=extensions)
        return render_template('page.html',
                               note_name=note_name,
                               note_description=note_description,
                               pagename=page_path,
                               content=content)
