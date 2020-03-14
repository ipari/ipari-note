from flask import redirect, render_template
from werkzeug.security import generate_password_hash

from app.config.config import is_require_setup, get_config, set_config
from app.setup import bp
from app.setup.forms import NoteForm, UserForm
from app.user.user import is_user_exists, set_user


@bp.route('/')
def route_setup():
    if is_require_setup():
        return redirect('/setup/note')
    elif not is_user_exists():
        return redirect('/setup/user')
    config = get_config()
    if 'require_setup' in config:
        del config['require_setup']
        set_config(config)
    return redirect('/setup/welcome')


@bp.route('/note', methods=['GET', 'POST'])
def route_setup_note():
    if not is_require_setup():
        return redirect('/setup')

    form = NoteForm()
    if form.validate_on_submit():
        value = {
            'title': form.title.data,
            'subtitle': form.subtitle.data,
        }
        config = get_config()
        config['note'].update(value)
        del config['require_setup']
        set_config(config)
        return redirect('/setup')

    value = get_config('note')
    form.title.data = value.get('title', '')
    form.subtitle.data = value.get('subtitle', '')
    return render_template('setup/note.html', form=form)


@bp.route('/user', methods=['GET', 'POST'])
def route_setup_user():
    if is_user_exists():
        return redirect('/setup')

    form = UserForm()
    if form.validate_on_submit():
        value = {
            'name': form.name.data,
            'email': form.email.data,
            'password': generate_password_hash(form.password.data),
        }
        set_user(value)
        return redirect('/setup')
    return render_template('setup/user.html', form=form)


@bp.route('/welcome')
def route_setup_welcome():
    return render_template('setup/welcome.html')
