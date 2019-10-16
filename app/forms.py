from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    email = StringField('Email Address:', validators=[DataRequired(), Email()])
    pw = PasswordField('Password:', validators=[DataRequired()])
    pw_confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('pw')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different name')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    about_me = TextAreaField('About me:', validators=[Length(min=1, max=140)])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Comment:', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

#
# class ImgForm(FlaskForm):
#     user_img = FileField('Upload photo:', validators=[FileRequired(), FileAllowed(['pdf','png','jpg','jpeg','gif'],
#                                                                                   'Only accept files with extension:'
#                                                                                   ' pdf, png, jpg, jpeg, gif')])
#     submit = SubmitField("Upload")
