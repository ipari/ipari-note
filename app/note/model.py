import html2text

from app import db
from app.crypto import encrypt
from app.note.permission import Permission


class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    path = db.Column(db.String(256), unique=True, nullable=False)
    encrypted_path = db.Column(db.String(256), nullable=False)
    filepath = db.Column(db.String(256), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    permission = db.Column(db.Enum(Permission), nullable=False)
    posted = db.Column(db.Boolean, nullable=False)
    pinned = db.Column(db.Boolean, nullable=False)
    created = db.Column(db.DateTime(timezone=True), nullable=False)
    updated = db.Column(db.DateTime(timezone=True), nullable=False)
    summary = db.Column(db.Text())
    tags = db.relationship('Tag')
    markdown = db.Column(db.Text)
    html = db.Column(db.Text)
    text = db.Column(db.Text)

    def __init__(self, meta, raw_md, html):
        self.update(meta, raw_md, html)

    def __repr__(self):
        return f'<Note> path: {self.path}, text: {self.text[:20]}'

    def update(self, meta, raw_md, html):
        self.title = meta.title
        self.path = meta.path
        self.encrypted_path = encrypt(meta.path)
        self.filepath = meta.filepath
        self.permission = Permission(meta.permission)
        self.posted = meta.posted
        self.pinned = meta.pinned
        self.created = meta.created or meta.updated
        self.updated = meta.updated
        self.summary = meta.summary
        self.html = html
        self.text = html2text.HTML2Text().handle(html)
        self.markdown = raw_md


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.String(256), db.ForeignKey('note.id'))
    tag = db.Column(db.String(256))

    def __init__(self, note, tag):
        self.note_id = note.id
        self.tag = tag

    def __repr__(self):
        return f'<Tag> note_id: {self.note_id}, text: {self.tag}'
