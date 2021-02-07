import html2text

from app import db
from .permission import Permission


class Note(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    path = db.Column(db.String(256), unique=True, nullable=False)
    filepath = db.Column(db.String(256), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    permission = db.Column(db.Enum(Permission), nullable=False)
    created = db.Column(db.DateTime(timezone=True), nullable=False)
    updated = db.Column(db.DateTime(timezone=True), nullable=False)
    summary = db.Column(db.Text())
    # tags = db.Column(db.ARRAY(db.String(256)))
    markdown = db.Column(db.Text)
    html = db.Column(db.Text)
    text = db.Column(db.Text)

    def __init__(self, meta, raw_md, html):
        self.update(html, meta)

    def __repr__(self):
        return f'<Note> path: {self.path}, text: {self.text[:20]}'

    def update(self, meta, raw_md, html):
        self.title = meta.title
        self.path = meta.path
        self.filepath = meta.filepath
        self.permission = meta.permission
        self.created = meta.created or meta.updated
        self.updated = meta.updated
        self.summary = meta.summary
        # self.tags = meta.tags
        self.html = html
        self.text = html2text.HTML2Text().handle(html)
        self.markdown = raw_md
