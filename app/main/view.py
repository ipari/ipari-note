import os
from flask import Blueprint, current_app, redirect, render_template, send_file, \
    url_for
from sqlalchemy import func

from app.note.model import Note, Tag
from app.note.note import get_base_meta, get_menu_list, get_page, get_tag_page,\
    error_page, update_all
from app.note.permission import Permission
from app.user.model import User


bp = Blueprint('main', __name__)


@bp.route('/')
def view_index():
    posts, next_url, prev_url = get_page()
    return render_template('posts.html',
                           meta=get_base_meta(),
                           menu=get_menu_list(),
                           pagename='',
                           posts=posts,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/posts/<int:page>')
def view_posts(page):
    posts, next_url, prev_url = get_page(page=page)
    return render_template('posts.html',
                           meta=get_base_meta(),
                           menu=get_menu_list(),
                           pagename='',
                           posts=posts,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/tags')
def view_tags():
    tag_info = Tag.query.join(Note, Tag.note_id == Note.id)\
        .filter(Note.permission == Permission.PUBLIC)\
        .group_by(Tag.tag)\
        .with_entities(Tag.tag, func.count())\
        .order_by(func.count().desc(), Tag.tag)\
        .all()
    return render_template('tags.html',
                           meta=get_base_meta(),
                           menu=get_menu_list(),
                           pagename='태그',
                           tag_info=tag_info)


@bp.route('/tags/<tag>')
def view_tag(tag):
    posts, next_url, prev_url = get_tag_page(tag)
    return render_template('posts.html',
                           meta=get_base_meta(),
                           menu=get_menu_list(),
                           pagename=f'#{tag}',
                           posts=posts,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/tags/<tag>/<int:page>')
def view_tag_posts(tag, page):
    posts, next_url, prev_url = get_tag_page(tag, page=page)
    return render_template('posts.html',
                           meta=get_base_meta(),
                           menu=get_menu_list(),
                           pagename=f'#{tag}',
                           posts=posts,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/update')
def view_update():
    if User.is_logged_in():
        update_all()
        return redirect('/')
    return error_page(page_path=None, message='로그인이 필요합니다.')


@bp.route('/<path:page_path>')
def route_to_note(page_path):
    return redirect(url_for('note.route_page', page_path=page_path))


@bp.route('/rss')
def route_rss():
    rss_path = os.path.join(current_app.instance_path, 'rss.xml')
    return send_file(rss_path)


@bp.route('/atom')
def route_atom():
    atom_path = os.path.join(current_app.instance_path, 'atom.xml')
    return send_file(atom_path)


@bp.route('/sitemap')
@bp.route('/sitemap.xml')
def route_sitemap():
    sitemap_path = os.path.join(current_app.instance_path, 'sitemap.xml')
    return send_file(sitemap_path)
