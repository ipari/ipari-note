from flask import Flask, redirect, url_for

from features import wiki
from features.config import config


app = Flask(__name__)


with app.app_context():
    theme = config('wiki')['template']
    app.static_folder = 'themes/{}/static'.format(theme)
    app.template_folder = 'themes/{}/templates'.format(theme)

    url_prefix = '/{}'.format(config('wiki')['base_url'])
    app.register_blueprint(wiki.blueprint, url_prefix=url_prefix)


@app.route("/")
def view_main():
    main_page = config('wiki')['main_page']
    return redirect(url_for('wiki.view_page', page_path=main_page))


if __name__ == '__main__':
    app.run()
