import markdown
import os
from datetime import datetime
from flask import current_app, flash, jsonify, request, render_template, \
    send_file, url_for
from urllib.parse import quote

from app import db
from app.utils import format_datetime
from app.config.model import Config
from app.user.model import User
from app.note.markdown import md_extensions
from app.note.model import Note, Tag
from app.note.permission import Permission


MARKDOWN_EXT = ('.md',)
HTML_EXT = ('.html', '.htm')
PAGE_ROOT = os.path.join('data', 'pages')
ROOT_PATH = os.path.realpath(PAGE_ROOT)


class NoteMeta(object):

    title = None
    path = None
    filepath = None
    permission = None
    posted = None
    pinned = None
    created = None
    updated = None
    tags = None
    summary = None

    def __init__(self, _meta, filepath):
        """

        Args:
            source: markdown.Markdown.Meta
        """
        self._meta = {k.lower(): v for k, v in _meta.items()}

        path, ext = os.path.splitext(filepath)
        self.title = path.split('/')[-1]
        self.path, _ = os.path.splitext(os.path.relpath(filepath, ROOT_PATH))
        self.filepath = filepath
        self.permission = self.parse_permission()
        self.posted = self.parse_posted()
        self.pinned = self.parse_pinned()
        self.created = self.parse_datetime('created')
        self.updated = self.parse_datetime('updated')
        self.tags = self.parse_tags('tags')
        self.summary = self._meta.get('summary', [''])[0]

        if self.updated is None:
            mtime_ts = int(os.path.getmtime(filepath))
            mtime_dt = datetime.fromtimestamp(mtime_ts)
            self.updated = mtime_dt

    @property
    def meta(self):
        return {
            'title': self.title,
            'path': self.path,
            'filepath': self.filepath,
            'permission': self.permission,
            'pinned': self.pinned,
            'created': self.created,
            'updated': self.updated,
            'tags': self.tags,
            'summary': self.summary,
        }

    def parse_tags(self, key):
        tags = self._meta.get(key, [])
        tags = [tag.strip() for tag in tags if tag.strip()]
        if not tags:
            return tags

        tags = tags[0].split(',')
        new_tags = []
        for tag in tags:
            tag = tag.strip()
            if tag.startswith('#'):
                tag = tag[1:]
            new_tags.append(tag)
        return new_tags

    def parse_datetime(self, key):
        value = self._meta.get(key, None)
        if not value:
            return None
        dt_str = value[0]
        dt_format = '%Y-%m-%d'
        if len(dt_str) > 10:
            dt_format = '%Y-%m-%d %H:%M:%S'
        try:
            return datetime.strptime(dt_str, dt_format)
        except ValueError:
            return None

    def parse_permission(self):
        v = self._meta.get('permission', None)
        if v is None:
            return Permission(0)
        return Permission(int(v[0]))

    def parse_posted(self):
        v = self._meta.get('posted', None)
        if v is None:
            return False
        return int(v[0])

    def parse_pinned(self):
        v = self._meta.get('pinned', None)
        if v is None:
            return False
        return int(v[0])


def render_markdown(raw_md):
    extensions = md_extensions()
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(raw_md)
    return html, md.Meta


def update_db(abs_path, feed_update=True):
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            raw_md = f.read()
    except FileNotFoundError:
        delete_db(abs_path, feed_update=feed_update)
        return

    html, meta = render_markdown(raw_md)
    meta = NoteMeta(meta, abs_path)
    path = meta.meta['path']

    note = Note.query.filter_by(path=path).first()
    if note:
        note.update(meta, raw_md, html)
    else:
        note = Note(meta, raw_md, html)
        db.session.add(note)

    tag_names = meta.meta.get('tags', [])
    Tag.query.filter_by(note_id=note.id).delete()
    for tag_name in tag_names:
        tag = Tag(note, tag_name)
        db.session.add(tag)

    db.session.commit()
    if feed_update:
        update_feed()


def delete_db(abs_path, feed_update=True):
    note_query = Note.query.filter_by(filepath=abs_path)
    note = note_query.first()
    Tag.query.filter_by(note_id=note.id).delete()
    note_query.delete()
    db.session.commit()
    if feed_update:
        update_feed()


def update_all():
    for subdir, dirs, files in os.walk(ROOT_PATH):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext not in MARKDOWN_EXT:
                continue
            path = os.path.join(subdir, file)
            update_db(path, feed_update=False)
    update_feed()


def serve_page(note, from_encrypted_path=False):
    if check_permission(note.permission, from_encrypted_path):
        meta = get_base_meta()
        meta = get_note_meta(note, meta=meta)
        menu = get_menu_list(page_path=note.path, page_exist=True)
        return render_template('page.html',
                               meta=meta,
                               menu=menu,
                               pagename=note.path,
                               content=note.html)
    return error_page(page_path=note.path)


def serve_file(page_path):
    path = os.path.join(ROOT_PATH, page_path)
    try:
        return send_file(path)
    except FileNotFoundError:
        pass


def check_permission(permission=Permission.PRIVATE, from_encrypted_path=False):
    if permission == Permission.PUBLIC or User.is_logged_in():
        return True
    if permission == Permission.LINK_ACCESS and from_encrypted_path:
        return True
    return False


def get_base_meta():
    note_config = Config.get()
    meta = dict()
    meta['note_title'] = note_config.get('note_title', '')
    meta['note_subtitle'] = note_config.get('note_subtitle', '')
    meta['note_description'] = note_config.get('note_description', '')
    meta['user_name'] = User.get_user_info('name')
    meta['year'] = datetime.now().year
    meta['ga_tracking_id'] = note_config.get('ga_tracking_id')
    meta['logged_in'] = User.is_logged_in()
    return meta


def get_note_meta(note, meta=None):
    meta = meta or dict()
    meta['created'] = note.created
    meta['updated'] = note.updated
    meta['permission'] = note.permission
    meta['is_page'] = True
    meta['encrypted_path'] = note.encrypted_path
    meta['tags'] = [tag.tag for tag in note.tags]
    return meta


def get_menu_list(page_path=None, page_exist=False, editable=True):
    items = []
    if User.is_logged_in():
        if page_path is not None and editable:
            # FIXME: 수정해야함
            base_url = 'note'
            url = f'/{base_url}/{page_path}/edit'
            if page_exist:
                items.append({'type': 'edit', 'url': url, 'label': '편집'})
            else:
                items.append({'type': 'write', 'url': url, 'label': '작성'})
        items.append({'type': 'list', 'url': '/note', 'label': '목록'})
        items.append({'type': 'tag', 'url': '/tags', 'label': '태그'})
        items.append({'type': 'config', 'url': '/config', 'label': '설정'})
        items.append({'type': 'logout', 'url': '/logout', 'label': '로그아웃'})
    else:
        items.append({'type': 'list', 'url': '/note', 'label': '목록'})
        items.append({'type': 'tag', 'url': '/tags', 'label': '태그'})
        items.append({'type': 'login', 'url': '/login', 'label': '로그인'})
    return items


def error_page(page_path, message=None):
    meta = get_base_meta()
    menu = get_menu_list(page_path=page_path)
    if message is None:
        if User.is_logged_in():
            message = '문서가 없습니다.'
        else:
            message = '문서가 없거나 권한이 없는 문서입니다.'
    flash(message)
    return render_template('page.html', meta=meta, menu=menu, pagename=page_path)


def edit_page(page_path):
    note = Note.query.filter_by(path=page_path).first()

    if note is None:
        # 새로운 노트를 생성할 때
        raw_md = get_template()
    else:
        filepath = note.filepath
        raw_md = read_md(filepath)
        if raw_md is None:
            # DB에 있는데 파일이 없으면 DB에서 해당 레코드 삭제
            Note.query.filter_by(path=page_path).delete()
            db.session.commit()
            raw_md = get_template()

    # ` 문자는 ES6에서 템플릿 문자로 사용되므로 escape 해줘야 한다.
    # https://developer.mozilla.org/ko/docs/Web/JavaScript/Reference/Template_literals
    raw_md = raw_md.replace('`', '\`')

    # FIXME: 수정해야함
    base_url = 'note'
    return render_template('edit.html',
                           pagename=page_path,
                           meta=get_base_meta(),
                           menu=get_menu_list(),
                           base_url=base_url,
                           raw_md=raw_md)


def read_md(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except (IOError, TypeError):
        return None


def update_page(page_path, raw_md):
    filepath = get_filepath(page_path, '.md')
    if raw_md:
        return save_page(filepath, raw_md)
    return delete_page(filepath)


def save_page(filepath, raw_md):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(raw_md)


def delete_page(filepath):
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
    # 빈 디렉터리 제거 (첫 2개는 data/pages)
    page_dir_length = len(PAGE_ROOT.split(os.path.sep))
    dirs = os.path.dirname(filepath).split(os.path.sep)[page_dir_length:]
    for x in range(len(dirs), 0, -1):
        subdir = os.path.join(PAGE_ROOT, *dirs[:x])
        try:
            if len(os.listdir(subdir)) == 0:
                os.rmdir(subdir)
        except OSError:
            continue


def save_file(page_path, file):
    filename = request.form.get('filename')
    if filename is None:
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'image-{now}.png'
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = '.png'
        filename += ext
    page_dir = '/'.join(page_path.split('/')[:-1])
    i = 0
    while True:
        if i > 0:
            filename = f'{name}-{i}{ext}'
        file_path = os.path.join(PAGE_ROOT, page_dir, filename)
        if not os.path.isfile(file_path):
            break
        i += 1
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    return jsonify(success=True, filename=filename)


def get_filepath(page_path, ext):
    path = os.path.join(PAGE_ROOT, page_path)
    return os.path.normpath(path) + ext


def get_template():
    # TODO: ---, ... 를 설정으로 옮겨야함
    template = f"""
    ---
    Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Permission: 0
    Tags: 
    Summary: 
    ---
    """
    template = [line.strip() for line in template.split('\n') if line]
    return "\n".join(template) + '\n'


def get_post_info_from_notes(list_of_note):
    posts = []
    for item in list_of_note:
        post = {
            'created': item.created,
            'updated': item.updated,
            'path': item.path,
            'permission': item.permission,
            'posted': item.posted,
            'pinned': item.pinned,
            'summary': item.summary,
            'tags': [tag.tag for tag in item.tags],
            'title': item.title,
        }
        posts.append(post)
    return posts


def get_posted_page(page=1):
    base_query = Note.query.filter_by(permission=Permission.PUBLIC, posted=1).\
        order_by(Note.pinned.desc(), Note.updated.desc())
    page = base_query.paginate(page, Config.get('post_per_page'), False)

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
    page = base_query.paginate(page, Config.get('post_per_page'), False)

    next_url = None
    prev_url = None
    if page.next_num:
        next_url = url_for('main.view_tag_posts', tag=tag, page=page.next_num)
    if page.prev_num:
        prev_url = url_for('main.view_tag_posts', tag=tag, page=page.prev_num)

    posts = get_post_info_from_notes(page.items)
    return posts, next_url, prev_url


###############################################################################
# Feed
###############################################################################


XML_Declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'


def update_feed():
    """
    https://validator.w3.org/feed/docs/rss2.html
    https://validator.w3.org/feed/docs/atom.html

    Returns:
    """

    notes = Note.query.filter_by(permission=Permission.PUBLIC, posted=1)\
        .order_by(Note.updated.desc()).all()
    sitemap_items, rss_items, atom_items = get_feed_from_notes(notes)

    now = datetime.now()
    timezone = Config.get('timezone')
    build_date_iso = format_datetime(now, style='iso-8601', timezone=timezone)
    build_date_rfc = format_datetime(now, style='rfc-822', timezone=timezone)

    update_sitemap(sitemap_items)
    update_rss(rss_items, build_date_rfc)
    update_atom(atom_items, build_date_iso)


def update_sitemap(sitemap_items):
    root_url = Config.get('url')
    sitemap = ''
    sitemap += XML_Declaration
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    base_locs = [
        f'{root_url}/',
        f'{root_url}/note',
        f'{root_url}/tags',
    ]
    for loc in base_locs:
        sitemap += f'    <url>\n        <loc>{loc}</loc>\n    </url>\n'
    sitemap += sitemap_items
    sitemap += '</urlset>'

    path = os.path.join(current_app.instance_path, 'sitemap.xml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sitemap)


def update_rss(rss_items, build_date):
    config = Config.get()

    rss2 = ''
    rss2 += XML_Declaration
    rss2 += f'<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
    rss2 += f'    <channel>\n'
    rss2 += f'        <title>{config["note_title"]}</title>\n'
    rss2 += f'        <link>{config["url"]}</link>\n'
    rss2 += f'        <atom:link href="{config["url"]}/rss" rel="self" type="application/rss+xml" />\n'
    rss2 += f'        <description>{config["note_description"]}</description>\n'
    rss2 += f'        <docs>{config["url"]}/rss</docs>\n'
    rss2 += f'        <generator>ipari-note</generator>\n'
    rss2 += f'        <lastBuildDate>{build_date}</lastBuildDate>\n'
    rss2 += rss_items
    rss2 += f'    </channel>\n'
    rss2 += f'</rss>'

    path = os.path.join(current_app.instance_path, 'rss.xml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(rss2)


def update_atom(atom_items, build_date):
    config = Config.get()
    user = User.get_user_info()

    atom = ''
    atom += XML_Declaration
    atom += f'<feed xmlns="http://www.w3.org/2005/Atom">\n'
    atom += f'    <title>{config["note_title"]}</title>\n'
    atom += f'    <subtitle>{config["note_subtitle"]}</subtitle>\n'
    atom += f'    <author>\n'
    atom += f'        <name>{user["name"]}</name>\n'
    atom += f'        <email>{user["email"]}</email>\n'
    atom += f'    </author>\n'
    atom += f'    <updated>{build_date}</updated>\n'
    atom += f'    <id>{config["url"]}/</id>\n'
    atom += f'    <link rel="alternate" href="{config["url"]}" />\n'
    atom += f'    <link rel="self" href="{config["url"]}/atom" />\n'
    atom += f'    <generator>ipari-note</generator>'
    atom += atom_items
    atom += f'</feed>'

    path = os.path.join(current_app.instance_path, 'atom.xml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(atom)


def get_feed_from_notes(notes):
    sitemap = ''
    rss2 = ''
    atom = ''

    name = User.get_user_info('name')
    email = User.get_user_info('email')
    root_url = Config.get('url')
    timezone = Config.get('timezone')
    # TODO: note_url_prefix 설정 적용
    note_url_prefix = 'note'

    for i, note in enumerate(notes):
        path = quote(note.path)
        item_url = f'{root_url}/{note_url_prefix}/{path}'

        # sitemap
        updated_iso = format_datetime(note.updated, style='iso-8601', timezone=timezone)
        sitemap += f'    <url>\n'
        sitemap += f'        <loc>{item_url}</loc>\n'
        sitemap += f'        <lastmod>{updated_iso}</lastmod>\n'
        sitemap += f'    </url>\n'

        if i > 10:
            continue

        # rss
        updated_rfc = format_datetime(note.updated, style='rfc-822', timezone=timezone)
        rss2 += f'        <item>\n'
        rss2 += f'            <title>{note.title}</title>\n'
        rss2 += f'            <author>{email} ({name})</author>\n'
        rss2 += f'            <pubDate>{updated_rfc}</pubDate>\n'
        rss2 += f'            <link>{item_url}</link>\n'
        rss2 += f'            <guid isPermaLink="false">{item_url}</guid>\n'
        rss2 += f'            <description>{note.summary}</description>\n'
        rss2 += f'        </item>\n'

        # atom
        published_iso = format_datetime(note.created, style='iso-8601', timezone=timezone)
        atom += f'    <entry>\n'
        atom += f'        <title>{note.title}</title>\n'
        atom += f'        <id>{item_url}</id>\n'
        atom += f'        <link rel="alternate" href="{item_url}" />\n'
        atom += f'        <published>{published_iso}</published>\n'
        atom += f'        <updated>{updated_iso}</updated>\n'
        atom += f'        <summary>{note.summary}</summary>\n'
        atom += f'    </entry>\n'

    return sitemap, rss2, atom
