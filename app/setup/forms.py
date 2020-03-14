from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class NoteForm(FlaskForm):
    title = StringField('제목')
    subtitle = StringField('부제')
    submit = SubmitField('다음')


class UserForm(FlaskForm):
    name = StringField('이름', [
        DataRequired(message='값을 입력해주세요')
    ])
    email = StringField('이메일', [
        DataRequired(message='값을 입력해주세요'),
        Email(message='올바른 이메일을 입력해주세요.')
    ])
    password = PasswordField('비밀번호', [
        DataRequired(message='값을 입력해주세요'),
        Length(min=4, message="4자 이상으로 입력해주세요.")
    ])
    password_confirm = PasswordField('비밀번호 확인', [
        DataRequired(message='값을 입력해주세요'),
        EqualTo('password', message='두 비밀번호가 일치해야합니다.'),
        Length(min=4, message="4자 이상으로 입력해주세요.")
    ])
    submit = SubmitField('완료')
