from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import exc
from grocerylistapp import bcrypt, db
from grocerylistapp.models import User, CompiledList
from grocerylistapp.forms import RecipeURLForm, CustomRecipeForm
from grocerylistapp.constructors import ChecklistCard

from grocerylistapp.account.forms import RegistrationForm, LoginForm, EditForm, ResetRequestForm, ResetPasswordForm, ChangePasswordForm
from grocerylistapp.account.utils import send_reset_email, send_validate_email

account = Blueprint('account', __name__)


@account.route('/home', methods=['GET', 'POST'])
def user_homepage():
    user_lists = CompiledList.query.filter_by(user_id=current_user.id)
    user_lists = [ChecklistCard(c, 3) for c in user_lists]

    url_form = RecipeURLForm(prefix='url')

    return render_template('user_home.html', user_lists=user_lists, url_form=url_form, grocery_lists=user_lists)


@account.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and not current_user.temporary:
        return redirect(url_for('main.home'))

    register_form = RegistrationForm()

    if register_form.validate_on_submit():
        print('here')
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        if not current_user.is_authenticated:
            user = User(username=register_form.username.data, email=register_form.email.data, password=hashed_password)
            db.session.add(user)
        else:
            user = User.query.get(current_user.id)
            user.username = register_form.username.data
            user.email = register_form.email.data
            user.password = hashed_password
            user.temporary = False

        try:
            db.session.commit()
            flash("Account created successfully!", "success")
            send_validate_email(user)
        except exc.IntegrityError as error:
            db.session.rollback()
            print(error.args)
            flash('Error. Username or email is already in use. Please choose a new one.', 'danger')

            return render_template('register.html', register_form=register_form)

        return redirect(url_for('account.login'))


    return render_template('register.html', register_form=register_form)


@account.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            flash('You are now logged in!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')

    return render_template('login.html', login_form=login_form)


@account.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@account.route('/settings', methods=['GET', 'POST'])
def settings():
    edit_form = EditForm(prefix='edit-info')
    password_form = ChangePasswordForm(prefix='change-password')
    if edit_form.validate_on_submit():
        print('form validated')
        user = User.query.get(current_user.id)
        try:
            user.username = edit_form.username.data
            db.session.commit()
        except exc.IntegrityError as error:
            db.session.rollback()
            flash('That username has already been taken.', 'danger')
            return redirect(url_for('account.settings'))

        try:
            user.email = edit_form.email.data
            db.session.commit()
        except exc.IntegrityError as error:
            db.session.rollback()
            flash('That email is in use for another account.', 'danger')
            return redirect(url_for('account.settings'))

        flash('account updated successfully!', 'success')
        return redirect(url_for('account.settings'))

    if password_form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, password_form.old_password.data):
            if password_form.new_password.data == password_form.old_password.data:  # can't change password if it's the same
                flash('Your new password must be different than your old one.', 'danger')
                return redirect(url_for('account.settings'))
            else:
                current_user.password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
                db.session.commit()
                flash('Your password has been changed successfully!', 'success')
                return redirect(url_for('account.settings'))
        else:
            flash('The password you entered does not match our records.', 'danger')
            return redirect(url_for('account.settings'))


    edit_form.username.data = current_user.username
    edit_form.email.data = current_user.email

    return render_template('settings.html', edit_form=edit_form, password_form=password_form)


@account.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    reset_form = ResetRequestForm()

    if reset_form.validate_on_submit():
        user = User.query.filter_by(email=reset_form.email.data).first()
        if not user:
            flash('Error: no account associated with this email. ', 'danger')
            return redirect(url_for('account.reset_request'))
        if not user.email_verified:
            flash('This user does not have a verified email address.', 'danger')
            return redirect(url_for('account.reset_request'))
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'success')
        return redirect(url_for('account.login'))

    return render_template('reset_request.html', reset_form=reset_form)


@account.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('account.reset_request'))
    reset_form = ResetPasswordForm()
    if reset_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(reset_form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('account.login'))

    return render_template('reset_token.html', reset_form=reset_form)


@account.route("/verify_email/<token>")
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        flash('This is an invalid validate request.', 'warning')
        return redirect(url_for('main.home'))
    user.email_validated = True
    db.session.commit()
    flash(f'The email account {user.email} has been validated!', 'success')
    return redirect(url_for('main.home'))
