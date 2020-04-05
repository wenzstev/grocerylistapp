from flask import url_for
from flask_mail import Message

from grocerylistapp import mail


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='groceryapp5@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
                    {url_for('account.reset_token', token=token, _external=True)}
                    If you did not make this request, please ignore this email. '''

    mail.send(msg)


def send_validate_email(user):
    token = user.get_validate_token()
    msg = Message('Verify Your Email', sender='groceryapp5@gmail.com', recipients=[user.email])
    msg.body = f'''To verify your email, please visit this link:
                    {url_for('account.verify_email', token=token, _external=True)}.
                    Please note: if you do not verify your email, you will be unable to reset your password.'''
    mail.send(msg)