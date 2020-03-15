from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField


class LoginForm(FlaskForm):
    referrer = HiddenField()
    email = StringField('이메일')
    password = PasswordField('비밀번호')
    submit = SubmitField('로그인')
