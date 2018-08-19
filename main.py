from flask import Flask, redirect, url_for

from features import archive, note, user
from features.config import config


app = Flask(__name__)
app.url_map.strict_slashes = False


with app.app_context():
    app.secret_key = config('secret')['key']

    theme = config('note')['template']
    app.static_folder = 'themes/{}/static'.format(theme)
    app.template_folder = 'themes/{}/templates'.format(theme)

    url_prefix = '/{}'.format(config('note')['base_url'])
    app.register_blueprint(archive.blueprint)
    app.register_blueprint(note.blueprint, url_prefix=url_prefix)
    app.register_blueprint(user.blueprint)


@app.route("/")
def view_main():
    main_page = config('note')['main_page']
    return redirect(url_for('note.view_page', page_path=main_page))


if __name__ == '__main__':
    app.run()
