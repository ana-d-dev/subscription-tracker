from wtforms import StringField, PasswordField
from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class RegistrationForm(FlaskForm):

    username = StringField('username', validators=[
        DataRequired(),
        Length(min=4, max=10, message="Username must contain between 4 and 10 characters."),
        Regexp(r"^[a-zA-Z0-9]+$", message="Username can contain only letters and numbers."),
    ])

    password = (PasswordField('password', validators=[
        DataRequired(),
        Length(min=8, max=21, message="Password must contain between 8 and 21 characters."),
        Regexp(
            r"^(?=(?:.*\d){2,})(?=(?:.*[a-zA-Z]){2,})(?=(?:.*[^a-zA-Z0-9]){2,}).*$",
               message="Password must contain at least 2 letters, 2 numbers, and 2 special characters."
        )
    ]))
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    login = SubmitField('Login')





