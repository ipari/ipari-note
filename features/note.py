import markdown
import os
from flask import Blueprint, current_app, render_template, send_file

from features.config import config, md_extensions


blueprint = Blueprint('note', __name__)


@blueprint.route('/<path:page_path>')
def view_page(page_path):
    base_path = os.path.join(current_app.root_path, 'pages', page_path)
    _, file_extension = os.path.splitext(page_path)
    print('ext: {}'.format(file_extension))
    if file_extension and file_extension != '.md':
        return send_file(base_path)

    data_path = base_path + '.md'
    with open(data_path, 'r') as f:
        extensions = md_extensions()
        title = '{} - {}'.format(page_path, config('note')['name'])
        content = markdown.markdown(f.read(), extensions=extensions)
        return render_template(
            'page.html', title=title, pagename=page_path, content=content)
