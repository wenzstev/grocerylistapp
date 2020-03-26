import secrets, json, pdfkit

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, make_response
from grocerylistapp.forms import CustomRecipeForm, RecipeURLForm

from grocerylistapp.models import RecipeList, RawLine, CleanedLine, CompiledList

from grocerylistapp import db

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def home():
    url_form = RecipeURLForm(prefix="url")
    custom_form = CustomRecipeForm(prefix="custom")

    grocery_lists = CompiledList.query.all()

    return render_template('home.html', title="Welcome!",
                           grocery_lists=grocery_lists,
                           url_form=url_form,
                           custom_form=custom_form)











