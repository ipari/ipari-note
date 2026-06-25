from flask import Blueprint, flash, redirect, render_template, request

from app.utils import dump_yaml, load_yaml


bp = Blueprint('config', __name__)


def _get_config_data():
    from app.config.model import CONFIG_PATH

    config = load_yaml(CONFIG_PATH)
    if config is None:
        config = {}

    config.setdefault('markdown', {})
    config.setdefault('note', {})
    config.setdefault('app', {})

    config['markdown'].setdefault('toc_marker', '')
    config['note'].setdefault('title', '')
    config['note'].setdefault('subtitle', '')
    config['note'].setdefault('description', '')
    config['app'].setdefault('theme', 'yaong')
    config['app'].setdefault('post_per_page', 5)
    config['app'].setdefault('ga_tracking_id', '')
    config['app'].setdefault('url', '')
    config['app'].setdefault('timezone', '+09:00')
    config.setdefault('aes_key', '')

    return config


def _update_config_data(form):
    config = _get_config_data()
    errors = []

    try:
        post_per_page = int(form.get('post_per_page', 5))
        if post_per_page < 1:
            errors.append('페이지당 포스트 수는 1 이상이어야 합니다.')
    except ValueError:
        post_per_page = config['app']['post_per_page']
        errors.append('페이지당 포스트 수는 숫자로 입력해주세요.')

    aes_key = form.get('aes_key', '').strip()
    if aes_key and len(aes_key) != 32:
        errors.append('AES 키는 비워두거나 32자로 입력해주세요.')

    if errors:
        return config, errors

    config['markdown']['toc_marker'] = form.get('md_toc_marker', '').strip()
    config['note']['title'] = form.get('note_title', '').strip()
    config['note']['subtitle'] = form.get('note_subtitle', '').strip()
    config['note']['description'] = form.get('note_description', '').strip()
    config['app']['theme'] = form.get('theme', '').strip() or 'yaong'
    config['app']['post_per_page'] = post_per_page
    config['app']['ga_tracking_id'] = form.get('ga_tracking_id', '').strip()
    config['app']['url'] = form.get('url', '').strip()
    config['app']['timezone'] = form.get('timezone', '').strip()
    config['aes_key'] = aes_key

    return config, []


@bp.route('/config', methods=['GET', 'POST'])
def route_config():
    from app.config.model import Config, CONFIG_PATH
    from app.note.note import get_base_meta, get_menu_list
    from app.user.model import User

    if not User.is_logged_in():
        flash('로그인이 필요합니다.')
        return redirect('/login')

    if request.method == 'POST':
        config, errors = _update_config_data(request.form)
        if errors:
            for error in errors:
                flash(error)
        else:
            dump_yaml(config, CONFIG_PATH)
            Config.update_config()
            flash('설정을 저장했습니다.')
            return redirect('/config')
    else:
        config = _get_config_data()

    return render_template('config.html',
                           meta=get_base_meta(),
                           menu=get_menu_list(),
                           pagename='설정',
                           config=config)
