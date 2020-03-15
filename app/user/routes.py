from flask import flash, redirect, render_template, request, session
from app.note.note import get_menu_list, get_note_meta
from app.user import bp
from app.user.forms import LoginForm
from app.user.user import is_logged_in, log_in


@bp.route('/user')
def route_user():
    return render_template('user.html')


@bp.route('/login', methods=['GET', 'POST'])
def route_login():
    if is_logged_in():
        return redirect('/')

    form = LoginForm()
    if request.method == 'GET':
        form.referrer = request.referrer
        meta = get_note_meta()
        menu = get_menu_list()
        return render_template('login.html', form=form, meta=meta, menu=menu)

    if log_in(form):
        if form.referrer:
            return redirect(form.referrer.data)
        return redirect('/')

    flash('입력한 값이 맞는지 확인해주세요.')
    return redirect('/login')


@bp.route('/logout')
def route_logout():
    if is_logged_in():
        session.pop('user')

    if request.referrer:
        return redirect(request.referrer)
    return redirect('/')
