import secrets, json, pdfkit

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, make_response
from flask_login import current_user
from grocerylistapp.forms import CustomRecipeForm, RecipeURLForm

from grocerylistapp.models import RecipeList, RawLine, CleanedLine, CompiledList

from grocerylistapp import db

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        if not current_user.temporary:
            return redirect(url_for('account.user_homepage'))
        else:
            flash('You are currently logged in as a guest and your account is temporary. Please register a permanent account to save your list and make additional lists!', 'info')
            return redirect(url_for('account.register'))


    url_form = RecipeURLForm(prefix="url")
    custom_form = CustomRecipeForm(prefix="custom")


    return render_template('home.html', title="Welcome!",
                           url_form=url_form,
                           custom_form=custom_form)











