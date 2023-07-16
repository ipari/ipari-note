import os
from flask import session
from werkzeug.security import check_password_hash

from app import db
from app.utils import load_yaml


USER_PATH = os.path.join(os.getcwd(), 'user.yml')


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(32), nullable=False)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

    def __repr__(self):
        return f'<User> name: {self.name}, email: {self.email}'

    @classmethod
    def update_user(cls):
        info = load_yaml(USER_PATH)
        if info is None:
            cls.query.first().delete()
        else:
            user = cls.query.first()
            if user is None:
                user = User(info['email'], info['password'], info['name'])
                db.session.add(user)
            else:
                for k, v in info.items():
                    setattr(user, k, v)
        db.session.commit()

    @classmethod
    def get_by_session(cls):
        email = session.get('email', None)
        if email is not None:
            return cls.query.filter_by(email=email).first()
        else:
            return None

    @classmethod
    def get_user_info(cls, column=None):
        user = cls.query.first()
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        if column:
            return row2dict(user)[column]
        return row2dict(user)

    @classmethod
    def login(cls, form):
        user = cls.query.filter_by(email=form.email.data).first()
        if user is None:
            return
        if form.email.data == user.email \
                and check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            session.permanent = True
            return True

    @staticmethod
    def logout():
        session.pop('email', None)

    @staticmethod
    def is_logged_in():
        return 'email' in session
