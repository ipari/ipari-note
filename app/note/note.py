import markdown
import os
from datetime import datetime
from flask import render_template, send_file, session

from app import db
from .markdown import md_extensions
from .model import Note, Tag
from .permission import Permission


MARKDOWN_EXT = ('.md', '.markdown')
HTML_EXT = ('.html', '.htm')
PAGE_ROOT = os.path.join('data', 'pages')
ROOT_PATH = os.path.realpath(PAGE_ROOT)


###############################################################################
# Class NoteMeta
###############################################################################
class NoteMeta(object):

    title = None
    path = None
    filepath = None
    permission = None
    created = None
    updated = None
    tags = None
    summary = None

    def __init__(self, _meta, filepath):
        """

        Args:
            source: markdown.Markdown.Meta
        """
        self._meta = _meta
        path, ext = os.path.splitext(filepath)
        self.title = path.split('/')[-1]
        self.path, _ = os.path.splitext(os.path.relpath(filepath, ROOT_PATH))
        self.filepath = filepath
        self.permission = self.parse_permission()
        self.created = self.parse_datetime('created')
        self.updated = self.parse_datetime('updated')
        self.tags = self.parse_tags('tags')
        self.summary = self._meta.get('summary', None)[0]

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
            'created': self.created,
            'updated': self.updated,
            'tags': self.tags,
            'summary': self.summary,
        }

    def parse_tags(self, key):
        tags = self._meta.get(key, [])
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
            return datetime.strptime(dt_str[0], dt_format)
        except ValueError:
            return None

    def parse_permission(self):
        v = self._meta.get('permission', None)
        if v is None:
            return Permission(0)
        return Permission(int(v[0]))


def get_abs_path(rel_path):
    path = os.path.join(PAGE_ROOT, rel_path)
    return os.path.normpath(path)


def get_md_path(rel_path):
    for ext in MARKDOWN_EXT:
        path = get_abs_path(rel_path) + ext
        if os.path.isfile(path):
            return path


def render_markdown(raw_md, abs_path):
    extensions = md_extensions()
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(raw_md)
    meta = NoteMeta(md.Meta, abs_path)
    return html, meta


def update_db(abs_path):
    with open(abs_path, 'r', encoding='utf-8') as f:
        raw_md = f.read()

    html, meta = render_markdown(raw_md, abs_path)
    path = meta.meta['path']

    note = Note.query.filter_by(path=path).first()
    if note:
        note.update(meta, raw_md, html)
    else:
        note = Note(meta, raw_md, html)
        db.session.add(note)

    tag_names = meta.meta.get('tags', [])
    Tag.query.filter_by(note_path=path).delete()
    for tag_name in tag_names:
        tag = Tag(note, tag_name)
        db.session.add(tag)

    db.session.commit()


def update_all():
    for subdir, dirs, files in os.walk(ROOT_PATH):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext not in MARKDOWN_EXT:
                continue
            path = os.path.join(subdir, file)
            update_db(path)


def serve_page(note):
    if check_permission(note.permission):
        return render_template('page.html', content=note.html)
    return '404 Not Found'


def serve_file(page_path):
    path = os.path.join(ROOT_PATH, page_path)
    return send_file(path)


def check_permission(permission=Permission.PRIVATE):
    if permission > Permission.PRIVATE:
        return True
    if permission == Permission.PRIVATE and 'email' in session:
        return True
    return False


# def render_page(page_path, meta):
#     md_path = get_md_path(page_path)
#     if md_path is None:
#         return error_page(page_path)
#
#     raw_md = get_raw_md(md_path)
#     content, _ = render_markdown(raw_md)
#     html_url = get_html_path(page_path)
#     meta.update(get_page_meta(page_path))
#     menu = get_menu_list(page_path=page_path, page_exist=True)
#     return render_template('page.html',
#                            meta=meta,
#                            menu=menu,
#                            pagename=page_path,
#                            content=content,
#                            html_url=html_url)


# import markdown
# from collections import defaultdict
# from datetime import datetime
# from flask import flash, jsonify, render_template, request, send_file, session
#
# from app.crypto import decrypt, encrypt
# from app.note.markdown import md_extensions
# from app.note.permission import *
# from app.user.user import get_user, is_logged_in
# from app.utils import config, dump_yaml, is_file_exist
#
#
# MARKDOWN_EXT = ('.md', '.markdown')
# HTML_EXT = ('.html', '.htm')
# PAGE_ROOT = os.path.join('data', 'pages')
#
# META_FILENAME = 'data/cache/meta.yml'
# META_PATH = os.path.normpath(os.path.join(os.getcwd(), META_FILENAME))
# TAG_FILENAME = 'data/cache/tag.yml'
# TAG_PATH = os.path.normpath(os.path.join(os.getcwd(), TAG_FILENAME))
# CONTENT_FILENAME = 'data/cache/content.yml'
# CONTENT_PATH = os.path.normpath(os.path.join(os.getcwd(), META_FILENAME))
#
#
# def get_note_meta():
#     note_config = config('note')
#     meta = dict()
#     meta['note_title'] = note_config.get('title', '')
#     meta['note_subtitle'] = note_config.get('subtitle', '')
#     meta['note_description'] = note_config.get('description', '')
#     meta['user_name'] = get_user('name')
#     meta['year'] = datetime.now().year
#     meta['ga_tracking_id'] = config('ga_tracking_id')
#     return meta
#
#
# def get_menu_list(page_path=None, page_exist=False, editable=True):
#     items = []
#     if is_logged_in():
#         if page_path is not None and editable:
#             base_url = config('note.base_url')
#             url = f'/{base_url}/{page_path}/edit'
#             if page_exist:
#                 items.append({'type': 'edit', 'url': url, 'label': '편집'})
#             else:
#                 items.append({'type': 'write', 'url': url, 'label': '작성'})
#         items.append({'type': 'archive', 'url': '/archive', 'label': '목록'})
#         items.append({'type': 'tag', 'url': '/tags', 'label': '태그'})
#         items.append({'type': 'config', 'url': '/config', 'label': '설정'})
#         items.append({'type': 'logout', 'url': '/logout', 'label': '로그아웃'})
#     else:
#         items.append({'type': 'archive', 'url': '/archive', 'label': '목록'})
#         items.append({'type': 'tag', 'url': '/tags', 'label': '태그'})
#         items.append({'type': 'login', 'url': '/login', 'label': '로그인'})
#     return items
#
#
# def render_page(page_path, meta):
#     md_path = get_md_path(page_path)
#     if md_path is None:
#         return error_page(page_path)
#
#     raw_md = get_raw_md(md_path)
#     content, _ = render_markdown(raw_md)
#     html_url = get_html_path(page_path)
#     meta.update(get_page_meta(page_path))
#     menu = get_menu_list(page_path=page_path, page_exist=True)
#     return render_template('page.html',
#                            meta=meta,
#                            menu=menu,
#                            pagename=page_path,
#                            content=content,
#                            html_url=html_url)
#
#
# def error_page(page_path, message=None):
#     meta = get_note_meta()
#     menu = get_menu_list(page_path=page_path)
#     if message is None:
#         if is_logged_in():
#             message = '문서가 없습니다.'
#         else:
#             message = '문서가 없거나 권한이 없는 문서입니다.'
#     flash(message)
#     return render_template('page.html', meta=meta, menu=menu, pagename=page_path)
#
#
# def serve_file(file_path):
#     if is_logged_in() or \
#             (request.referrer and request.url_root in request.referrer):
#         path = os.path.join('..', PAGE_ROOT, file_path)
#         path = os.path.normpath(path)
#         try:
#             return send_file(path)
#         except FileNotFoundError:
#             pass
#     return error_page(file_path)
#
#
# def serve_page(page_path):
#     # 노트는 권한에 따라 다르게 처리한다.
#     permission = get_permission(page_path)
#     meta = get_note_meta()
#     meta['is_page'] = True
#     meta['logged_in'] = is_logged_in()
#     meta['permission'] = permission
#     meta['link'] = encrypt_url(page_path)
#     if is_logged_in() or permission == Permission.PUBLIC:
#         return render_page(page_path, meta)
#     elif permission == Permission.LINK_ACCESS:
#         if decrypt(session.get('key')) == page_path:
#             return render_page(page_path, meta)
#     return error_page(page_path)
#
#
# def config_page(page_path, form):
#     if not is_logged_in():
#         message = "페이지 설정을 변경하지 못하였습니다."
#         return error_page(page_path=page_path, message=message)
#
#     if 'permission' in form:
#         permission = int(form['permission'])
#         set_permission(page_path, permission)
#     return serve_page(page_path)
#
#
# def save_page(page_path, raw_md):
#     md_path = get_md_path(page_path)
#     if md_path is None:
#         md_path = norm_page_path(page_path) + MARKDOWN_EXT[0]
#     # 문서 기록
#     os.makedirs(os.path.dirname(md_path), exist_ok=True)
#     with open(md_path, 'w', encoding='utf-8') as f:
#         f.write(raw_md)
#     # 메타 업데이트
#     update_page_meta(page_path)
#
#
# def delete_page(page_path):
#     # 퍼미션 제거
#     delete_permission(page_path)
#
#     # 파일 제거
#     file_path = get_md_path(page_path)
#     os.remove(file_path)
#
#     # 메타 업데이트
#     update_page_meta(page_path)
#
#     # 빈 디렉터리 제거 (첫 2개는 data/pages)
#     page_dir_length = len(PAGE_ROOT.split(os.path.sep))
#     dirs = os.path.dirname(file_path).split(os.path.sep)[page_dir_length:]
#     for x in range(len(dirs), 0, -1):
#         subdir = os.path.join(PAGE_ROOT, *dirs[:x])
#         try:
#             if len(os.listdir(subdir)) == 0:
#                 os.rmdir(subdir)
#         except OSError:
#             continue
#
#
# def edit_page(page_path):
#     md_path = get_md_path(page_path)
#     base_url = config('note.base_url')
#     raw_md = get_raw_md(md_path)
#     # ` 문자는 ES6에서 템플릿 문자로 사용되므로 escape 해줘야 한다.
#     # https://developer.mozilla.org/ko/docs/Web/JavaScript/Reference/Template_literals
#     raw_md = raw_md.replace('`', '\`')
#     return render_template('edit.html',
#                            pagename=page_path,
#                            meta=get_note_meta(),
#                            menu=get_menu_list(),
#                            base_url=base_url,
#                            raw_md=raw_md)
#
#
# def save_file(page_path, file):
#     filename = request.form.get('filename')
#     if filename is None:
#         now = datetime.now().strftime('%Y%m%d%H%M%S')
#         filename = f'image-{now}.png'
#     name, ext = os.path.splitext(filename)
#     if not ext:
#         ext = '.png'
#         filename += ext
#     page_dir = '/'.join(page_path.split('/')[:-1])
#     i = 0
#     while True:
#         if i > 0:
#             filename = f'{name}-{i}{ext}'
#         file_path = os.path.join(PAGE_ROOT, page_dir, filename)
#         if not is_file_exist(file_path):
#             break
#         i += 1
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)
#     file.save(file_path)
#     return jsonify(success=True, filename=filename)
#
#
# def norm_page_path(page_path):
#     path = os.path.join(PAGE_ROOT, page_path)
#     return os.path.normpath(path)
#
#
# def get_md_path(page_path):
#     for ext in MARKDOWN_EXT:
#         path = norm_page_path(page_path) + ext
#         if is_file_exist(path):
#             return path
#
#
# def get_html_path(page_path):
#     for ext in HTML_EXT:
#         path = norm_page_path(page_path) + ext
#         if is_file_exist(path):
#             return page_path + ext
#
#
# def encrypt_url(page_path):
#     url_root = request.url_root
#     base_url = config('note.base_url')
#     url = f'{url_root}{base_url}/{encrypt(page_path)}'
#     return url
#
#
# def get_raw_md(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return f.read()
#     except (IOError, TypeError):
#         template = f"""
#         Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#         Summary:
#         Tags:
#         """
#         template = [line.strip() for line in template.split('\n') if line]
#         return "\n".join(template) + '\n'
#
#
# def render_markdown(raw_md):
#     extensions = md_extensions()
#     md = markdown.Markdown(extensions=extensions)
#     html = md.convert(raw_md)
#     meta = process_page_meta(md.Meta)
#     return html, meta
#
#
# def iterate_pages(extension=False):
#     for root, subdirs, files in os.walk(PAGE_ROOT):
#         for file in files:
#             name, ext = os.path.splitext(file)
#             if ext not in MARKDOWN_EXT:
#                 continue
#             abs_path = os.path.join(root,
#                                     file if extension else name)
#             page_path = os.path.relpath(abs_path, PAGE_ROOT)
#             yield page_path
#
#
# def get_page_list(page_paths=None, sort_key=None, reverse=False, pinned=False):
#     """ 페이지 목록
#
#     Args:
#         page_paths: page_path 목록
#         sort_key: 정렬 키
#         reverse: 정렬 역순 여부
#         pinned: 고정된 페이지 포함 여부
#
#     Returns: list of dict
#     """
#
#     def make_page_info(page_path, is_pinned=False):
#         permission = permissions.get(page_path, 0)
#         if not is_logged_in() and permission != Permission.PUBLIC:
#             return
#         page = {
#             'title': page_path.split('/')[-1],
#             'path': page_path,
#             'permission': permission,
#             'is_pinned': is_pinned
#         }
#         page_meta = page_metas.get(page_path, {})
#         page.update(page_meta)
#         return page
#
#     page_paths = page_paths or iterate_pages()
#     sort_key = sort_key or 'updated'
#     permissions = get_permission()
#     page_metas = get_page_meta()
#     pinned_page_paths = config('note.pinned_pages') or []
#
#     pages = []
#     for page_path in page_paths:
#         if pinned and page_path in pinned_page_paths:
#             continue
#         page = make_page_info(page_path)
#         if page:
#             pages.append(page)
#
#     try:
#         pages.sort(key=lambda x: x[sort_key], reverse=reverse)
#     except KeyError:
#         update_all_page_meta()
#         return get_page_list(page_paths=page_paths,
#                              sort_key=sort_key,
#                              reverse=reverse)
#     if pinned and pinned_page_paths:
#         pinned_pages = []
#         for page_path in pinned_page_paths:
#             page = make_page_info(page_path, is_pinned=True)
#         if page:
#             pinned_pages.append(page)
#         pages = pinned_pages + pages
#
#     return pages
#
#
# def get_tag_list():
#     tag_metas = get_tag_meta()
#     permissions = get_permission()
#     result = []
#     for tag, tag_info in tag_metas.items():
#         tag_info['tag'] = tag
#         tag_info['pages'] = [
#             page for page in tag_info['pages']
#             if is_logged_in() or permissions.get(page, 0) == Permission.PUBLIC
#         ]
#         if len(tag_info['pages']) > 0:
#             result.append(tag_info)
#
#     try:
#         result.sort(key=lambda x: x['created'])
#         result.sort(key=lambda x: x['updated'], reverse=True)
#         result.sort(key=lambda x: len(x['pages']), reverse=True)
#     except KeyError:
#         update_all_page_meta()
#         return get_tag_list()
#     return result
#
#
# def get_page_list_in_tag(tag):
#     tag_meta = get_tag_meta(tag)
#     page_paths = tag_meta.get('pages', [])
#     return get_page_list(page_paths=page_paths, reverse=True)
#
#
# def get_page_meta(page_path=None):
#     try:
#         with open(META_PATH, 'r', encoding='utf-8') as f:
#             data = yaml.safe_load(f)
#     except IOError:
#         update_all_page_meta()
#         return get_page_meta(page_path=page_path)
#     if page_path is None:
#         return data
#     return data.get(page_path, {})
#
#
# def get_tag_meta(tag=None):
#     try:
#         with open(TAG_PATH, 'r', encoding='utf-8') as f:
#             data = yaml.safe_load(f)
#     except IOError:
#         update_all_page_meta()
#         return get_tag_meta(tag=tag)
#     if tag is None:
#         return data
#     return data.get(tag, {})
#
#
# def process_page_meta(prev_meta):
#     meta = {}
#     for k, v in prev_meta.items():
#         v = prev_meta[k][0]
#         if not v:
#             continue
#         # 타입에 따른 처리
#         if k == 'tags':
#             tags = []
#             for tag in v.split(','):
#                 tag = tag.strip()
#                 if tag.startswith('#'):
#                     tag = tag[1:]
#                 tags.append(tag)
#             v = tags
#
#         elif k in ('created', 'updated'):
#             try:
#                 v = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
#             except ValueError:
#                 v = datetime.strptime(v, '%Y-%m-%d')
#         if v:
#             meta[k] = v
#     return meta
#
#
# def make_page_meta(page_path, meta=None):
#     md_path = get_md_path(page_path)
#     if meta is None:
#         raw_md = get_raw_md(md_path)
#         _, meta = render_markdown(raw_md)
#     if md_path and 'updated' not in meta:
#         mtime_ts = int(os.path.getmtime(md_path))
#         mtime_dt = datetime.fromtimestamp(mtime_ts)
#         meta['updated'] = mtime_dt
#     meta['cached'] = int(datetime.now().timestamp())
#     return meta
#
#
# def save_meta(data):
#     dump_yaml(data, META_PATH)
#
#
# def save_tag(data):
#     data = dict(data)
#     dump_yaml(data, TAG_PATH)
#
#
# def update_all_tag_meta(page_metas):
#     tag_metas = defaultdict(lambda: {
#         'pages': [], 'created': datetime.max, 'updated': datetime.min})
#     for page_path, page_meta in page_metas.items():
#         tags = page_meta.get('tags', [])
#         updated = page_meta.get('updated')
#         created = page_meta.get('created', updated)
#         for tag in tags:
#             tag_metas[tag]['pages'].append(page_path)
#             tag_metas[tag]['created'] = min(created, tag_metas[tag]['created'])
#             tag_metas[tag]['updated'] = max(updated, tag_metas[tag]['updated'])
#     save_tag(tag_metas)
#
#
# def update_page_meta(page_path):
#     page_metas = get_page_meta()
#     md_path = get_md_path(page_path)
#     page_meta = make_page_meta(page_path)
#     if md_path is None and page_path in page_metas:
#         del page_metas[page_path]
#     else:
#         page_metas[page_path] = page_meta
#     save_meta(page_metas)
#     update_all_tag_meta(page_metas)
#
#
# def update_all_page_meta():
#     page_metas = {}
#     for page_path in iterate_pages():
#         page_metas[page_path] = make_page_meta(page_path)
#     save_meta(page_metas)
#     update_all_tag_meta(page_metas)
