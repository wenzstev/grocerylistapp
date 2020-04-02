from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import exc
from grocerylistapp import bcrypt, db
from grocerylistapp.models import User, CompiledList
from grocerylistapp.forms import RecipeURLForm, CustomRecipeForm
from grocerylistapp.constructors import ChecklistCard

from grocerylistapp.account.forms import RegistrationForm, LoginForm


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
    grocery_lists = CompiledList.query.filter_by(user_id=current_user.id).all()

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
        except exc.IntegrityError as error:
            db.session.rollback()
            print(error.args)
            flash('Error. Username or email is already in use. Please choose a new one.', 'danger')
            return render_template('register.html', register_form=register_form, grocery_lists=grocery_lists)

        return redirect(url_for('account.login'))

    return render_template('register.html', register_form=register_form, grocery_lists=grocery_lists)


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