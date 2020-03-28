from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email


class RegistrationForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    password_confirm = PasswordField("Confirm Password: ", validators=[DataRequired(), EqualTo('password')])
    email = StringField("Email: ", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username: ")
    password = PasswordField("Password: ")
    submit = SubmitField("Submit")
