from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length


class DigitRequired:
    def __init__(self, message=None):
        if not message:
            message = "You must include at least one number."
        self.message = message

    def __call__(self, form, field):
        if not any(char.isdigit() for char in field.data):
            raise ValidationError(self.message)


class SymbolRequired:
    def __init__(self, message=None, accepted_syms=None):
        if not accepted_syms:
            accepted_syms = {'!', '@', '#', '$', '%', '^', '&', '*', '-', '+', '+', '_', '|', '~', '?'}
        self.accepted_syms = accepted_syms

        if not message:
            message = f"You must include at least one of the following symbols: {', '.join(self.accepted_syms)}."
        self.message = message

    def __call__(self, form, field):
        if not any(sym in field.data for sym in self.accepted_syms):
            raise ValidationError(self.message)


PasswordValidators = [DataRequired(), SymbolRequired(), DigitRequired(), Length(min=8, max=20)]


class RegistrationForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=PasswordValidators)
    password_confirm = PasswordField("Confirm Password: ", validators=[DataRequired(), EqualTo('password')])
    email = StringField("Email: ", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username: ")
    password = PasswordField("Password: ")
    submit = SubmitField("Submit")


class EditForm(FlaskForm):
    username = StringField("Username: ")
    email = StringField("Email: ", validators=[Email()])
    submit = SubmitField("Submit Changes")


class ResetRequestForm(FlaskForm):
    email = StringField("Email: ", validators=[Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=PasswordValidators)
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=PasswordValidators)
    new_password_confirm = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


class DeleteTemporaryForm(FlaskForm):
    submit = SubmitField('Delete Temporary Users')