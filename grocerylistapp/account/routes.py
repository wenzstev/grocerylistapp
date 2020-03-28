from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import exc
from grocerylistapp import bcrypt, db
from grocerylistapp.models import User

from grocerylistapp.account.forms import RegistrationForm, LoginForm


account = Blueprint('account', __name__)


@account.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        print('here')
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        user = User(username=register_form.username.data, email=register_form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully!", "success")
            login_user(user)
        except exc.IntegrityError as error:
            db.session.rollback()
            print(error.args)
            flash('Error. Username or email is already in use. Please choose a new one.', 'danger')
            return render_template('register.html', register_form=register_form)

        return redirect(url_for('main.home'))

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