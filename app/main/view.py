from flask import Blueprint, render_template, url_for

from app import db
from app.note.model import Note, Tag
from app.note.note import update_all, get_base_meta, get_menu_list
from app.note.permission import Permission


bp = Blueprint('main', __name__)


POST_PER_PAGE = 5


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
                           pagename='',
                           posts=posts,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/tags')
def view_tags():
    from sqlalchemy import func
    tag_info = Tag.query.with_entities(Tag.tag, func.count(Tag.note_id))\
        .group_by(Tag.tag)\
        .order_by(func.count(Tag.note_id).desc(), Tag.tag)\
        .all()
    return tag_info


@bp.route('/tags/<tag>')
def view_tag(tag):
    posts, next_url, prev_url = get_tag_page(tag)
    return render_template('posts.html',
                           meta=get_base_meta(),
                           pagename=f'#{tag}',
                           posts=posts,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/tags/<tag>/<int:page>')
def view_tag_posts(tag, page):
    posts, next_url, prev_url = get_tag_page(tag, page=page)
    return render_template('posts.html',
                           meta=get_base_meta(),
                           pagename=f'#{tag}',
                           posts=posts,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/update')
def view_update():
    update_all()
    return 'update'


def get_post_info_from_notes(list_of_note):
    posts = []
    for item in list_of_note:
        post = {
            'created': item.created,
            'updated': item.updated,
            'path': item.path,
            'permission': item.permission,
            'pinned': item.pinned,
            'summary': item.summary,
            'tags': [tag.tag for tag in item.tags],
            'title': item.title,
        }
        posts.append(post)
    return posts


def get_page(page=1):
    base_query = Note.query.filter_by(permission=Permission.PUBLIC).\
        order_by(Note.pinned.desc(), Note.updated.desc())
    page = base_query.paginate(page, POST_PER_PAGE, False)

    next_url = None
    prev_url = None
    if page.next_num:
        next_url = url_for('main.view_posts', page=page.next_num)
    if page.prev_num:
        prev_url = url_for('main.view_posts', page=page.prev_num)

    posts = get_post_info_from_notes(page.items)
    return posts, next_url, prev_url


def get_tag_page(tag, page=1):
    base_query = Note.query.join(Tag, Note.id == Tag.note_id)\
        .filter(Tag.tag == tag, Note.permission == Permission.PUBLIC)\
        .order_by(Note.updated.desc())
    page = base_query.paginate(page, POST_PER_PAGE, False)

    next_url = None
    prev_url = None
    if page.next_num:
        next_url = url_for('main.view_tag_posts', tag=tag, page=page.next_num)
    if page.prev_num:
        prev_url = url_for('main.view_tag_posts', tag=tag, page=page.prev_num)

    posts = get_post_info_from_notes(page.items)
    return posts, next_url, prev_url
