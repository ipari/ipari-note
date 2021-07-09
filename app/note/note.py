import markdown
import os
from datetime import datetime
from flask import flash, jsonify, request, render_template, send_file, url_for

from app import db
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


def update_db(abs_path):
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            raw_md = f.read()
    except FileNotFoundError:
        delete_db(abs_path)
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


def delete_db(abs_path):
    note_query = Note.query.filter_by(filepath=abs_path)
    note = note_query.first()
    Tag.query.filter_by(note_id=note.id).delete()
    note_query.delete()
    db.session.commit()


def update_all():
    for subdir, dirs, files in os.walk(ROOT_PATH):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext not in MARKDOWN_EXT:
                continue
            path = os.path.join(subdir, file)
            update_db(path)


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
    template = f"""
    Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Summary:
    Tags:
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
