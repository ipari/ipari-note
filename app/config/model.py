import os
from app import db
from app.utils import load_yaml


CONFIG_PATH = os.path.join(os.getcwd(), 'config.yml')


class Config(db.Model):
    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    md_toc_marker = db.Column(db.String(64), nullable=False)
    note_title = db.Column(db.String(256))
    note_subtitle = db.Column(db.String(256))
    note_description = db.Column(db.String(1024))
    theme = db.Column(db.String(64), nullable=False)
    post_per_page = db.Column(db.Integer, nullable=False)
    ga_tracking_id = db.Column(db.String(64))
    url = db.Column(db.String(128))
    timezone = db.Column(db.String(6))
    aes_key = db.Column(db.String(32), nullable=False)

    def __init__(self, md_toc_marker=None, note_title=None, note_subtitle=None,
                 note_description=None, theme=None, post_per_page=None,
                 ga_tracking_id=None, url=None, timezone=None, aes_key=None):
        self.md_toc_marker = md_toc_marker
        self.note_title = note_title
        self.note_subtitle = note_subtitle
        self.note_description = note_description
        self.theme = theme
        self.post_per_page = post_per_page
        self.ga_tracking_id = ga_tracking_id
        self.url = url
        self.timezone = timezone
        self.aes_key = aes_key

    def __repr__(self):
        return f'<Config>'

    @classmethod
    def update_config(cls):
        info = load_yaml(CONFIG_PATH)
        if info is None:
            cls.query.first().delete()
        else:
            params = {
                'md_toc_marker': info['markdown']['toc_marker'],
                'note_title': info['note']['title'],
                'note_subtitle': info['note']['subtitle'],
                'note_description': info['note']['description'],
                'theme': info['app']['theme'],
                'post_per_page': info['app']['post_per_page'],
                'ga_tracking_id': info['app']['ga_tracking_id'],
                'url': info['app']['url'],
                'timezone': info['app']['timezone'],
                'aes_key': info['aes_key'],
            }
            config = cls.query.first()
            if config is None:
                config = Config(**params)
                db.session.add(config)
            else:
                for k, v in params.items():
                    setattr(config, k, v)
        db.session.commit()

    @classmethod
    def get(cls, column=None):
        config = cls.query.first()
        row2dict = lambda r: {c.name: getattr(r, c.name) for c in r.__table__.columns}
        if column:
            return row2dict(config)[column]
        return row2dict(config)
