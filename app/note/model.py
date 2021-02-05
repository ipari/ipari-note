from .. import db
from .note import update_db
from .permission import Permission


class Note(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    path = db.Column(db.String(256), unique=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    permission = db.Column(db.Enum(Permission), nullable=False)
    created = db.Column(db.DateTime(timezone=True), nullable=False)
    updated = db.Column(db.DateTime(timezone=True), nullable=False)
    summary = db.Column(db.Text())
    tags = db.Column(db.ARRAY(db.String(256)))
    markdown = db.Column(db.Text)
    html = db.Column(db.Text)
    text = db.Column(db.Text)

    def __init__(self, rel_path):
        update_db(rel_path)



    def __repr__(self):
        return f'<Note> path: {self.path}, text: {self.text[:20]}'
