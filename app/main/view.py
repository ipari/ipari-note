from flask import Blueprint, render_template, url_for

from app import db
from app.note.model import Note, Tag
from app.note.note import update_all, get_base_meta
from app.note.permission import Permission


bp = Blueprint('main', __name__)


POST_PER_PAGE = 5


@bp.route('/')
def view_index():
    posts, next_url, prev_url = get_page(page=1)
    return render_template('posts.html',
                           meta=get_base_meta(),
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


@bp.route('/update')
def view_update():
    update_all()
    return 'update'


def get_page(page=0):
    base_query = Note.query.filter_by(permission=Permission.PUBLIC).\
        order_by(Note.pinned.desc(), Note.updated.desc())
    page = base_query.paginate(page, POST_PER_PAGE, False)

    next_url = None
    prev_url = None
    if page.next_num:
        next_url = url_for('main.view_posts', page=page.next_num)
    if page.prev_num:
        prev_url = url_for('main.view_posts', page=page.prev_num)

    posts = []
    for item in page.items:
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

    return posts, next_url, prev_url
