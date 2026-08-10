from wtforms import StringField, PasswordField
from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class RegistrationForm(FlaskForm):

    username = StringField('username', validators=[
        DataRequired(),
        Length(min=4, max=10),
        Regexp(r"^[a-zA-Z0-9]+$"),
    ])

    password = (PasswordField('password', validators=[
        DataRequired(),
        Length(min=8, max=21),
        Regexp(r"^(?=(?:.*\d){2,})(?=(?:.*[a-zA-Z]){2,})(?=(?:.*[^a-zA-Z0-9]){2,}).*$")
    ]))
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    login = SubmitField('Login')





