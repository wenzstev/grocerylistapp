import json, pdfkit

from flask import Blueprint, redirect, url_for, flash, render_template, request, jsonify, make_response, abort
from flask_login import current_user

from grocerylistapp import db
from grocerylistapp.models import CompiledList, CleanedLine, RecipeList, RawLine
from grocerylistapp.forms import CustomRecipeForm, RecipeURLForm
from grocerylistapp.constructors import CompiledIngredientLine, create_recipe_from_url, create_recipe_from_text

from grocerylistapp.checklist.forms import ExportToPDFForm, ExportToEmailForm
from grocerylistapp.checklist.utils import sort_list, email_list, create_list

checklist = Blueprint('checklist', __name__)


@checklist.route('/list/<string:hex_name>', methods=['GET', 'POST'])
def compiled_list(hex_name):
    recipe_form = RecipeURLForm(prefix="recipe")
    custom_recipe_form = CustomRecipeForm(prefix="custom-recipe")
    export_to_pdf_form = ExportToPDFForm(prefix="export-pdf")
    export_to_email_form = ExportToEmailForm(prefix="email")

    comp_list = CompiledList.query.filter_by(hex_name=hex_name).first_or_404()
    list_lines = CleanedLine.query.filter_by(list=comp_list).all()
    sort_list(list_lines)

    recipe_list = RecipeList.query.filter_by(complist=comp_list).all()

    if recipe_form.validate_on_submit():
        new_recipe = create_recipe_from_url(recipe_form.url.data)
        return redirect(url_for('recipe.clean_recipe', list_name=hex_name, new_recipe=new_recipe.hex_name))

    if custom_recipe_form.validate_on_submit():
        new_recipe = create_recipe_from_text("Untitled Recipe", custom_recipe_form.recipe_lines.data)
        new_recipe.complist = comp_list

        return redirect(url_for('recipe.clean_recipe', list_name=comp_list.hex_name, new_recipe=new_recipe.hex_name))

    if export_to_email_form.validate_on_submit():
        email_list(export_to_email_form.email.data, comp_list, list_lines, recipe_list)
        flash('Email sent successfully!', 'success')

        return redirect(url_for('list.compiled_list', hex_name=hex_name))


    list_lines = [CompiledIngredientLine(line) for line in list_lines]


    # reverse to put "additional ingredients" on bottom
    recipe_list.reverse()

    grocery_lists = CompiledList.query.filter_by(user_id=current_user.id)

    return render_template('list_page.html', grocery_lists=grocery_lists, comp_list=comp_list,
                           list_lines=list_lines, recipe_form=recipe_form,
                           recipe_list=recipe_list, custom_recipe_form=custom_recipe_form,
                           export_to_pdf_form=export_to_pdf_form, export_to_email_form=export_to_email_form)


@checklist.route('/list/create', methods=['GET', 'POST'])
def create_list_page():
    grocery_lists = CompiledList.query.filter_by(user_id=current_user.id).all()
    url_form = RecipeURLForm(prefix='url')
    custom_form = CustomRecipeForm(prefix='custom')

    return render_template('create_list.html', grocery_lists=grocery_lists, url_form=url_form, custom_form=custom_form)


@checklist.route('/list/create/<string:method>', methods=['GET', 'POST'])
def create_methods(method):
    new_list = create_list(current_user.id)

    # figure out how the list was created
    print(request.form)

    if method == 'blank':
        return redirect(url_for('checklist.compiled_list', hex_name=new_list.hex_name))

    elif method == 'url':
        # take the url input and parse for ingredient lines
        new_recipe = create_recipe_from_url(request.form.get('url-url', '', type=str))
        new_recipe.complist = new_list

    elif method == 'manual':
        new_recipe = create_recipe_from_text('Untitled Recipe', request.form.get('custom-recipe_lines', '', type=str))
        new_recipe.complist = new_list

    else:
        abort(404)

    return redirect(url_for('recipe.clean_recipe', list_name=new_list.hex_name, new_recipe=new_recipe.hex_name))



@checklist.route('/list/<string:hex_name>/delete', methods=['GET', 'POST'])
def delete(hex_name):
    list_to_delete = CompiledList.query.filter_by(hex_name=hex_name).first_or_404()
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('main.home'))


@checklist.route('/list/rename', methods=['GET', 'POST'])
def change_name():
    list_to_rename = CompiledList.query.filter_by(hex_name=request.form.get('list', '', type=str)).first_or_404()
    list_to_rename.name = request.form.get('name', 'ERROR', type=str)
    db.session.commit()

    return jsonify(name=list_to_rename.name)


@checklist.route('/list/reorder', methods=['POST'])
def reorder_list():
    list_to_reorder = CompiledList.query.filter_by(hex_name=request.form.get('list', '', type=str)).first_or_404()
    list_lines_to_reorder = CleanedLine.query.filter_by(list=list_to_reorder)
    new_order = json.loads(request.form.get('order'))
    print(new_order)
    print(type(new_order))

    for line in list_lines_to_reorder:
        print(line.hex_id)
        line.index_in_list = new_order[line.hex_id]
        print("new index for " + line.hex_id + " is " + str(line.index_in_list))

    db.session.commit()

    return jsonify(order=new_order)


@checklist.route('/list/<string:hex_name>/print', methods=['POST'])
def print_list(hex_name):
    print(request.form)
    list = CompiledList.query.filter_by(hex_name=hex_name).first_or_404()
    list_lines = CleanedLine.query.filter_by(list=list).all()
    sort_list(list_lines)

    list_lines = [CompiledIngredientLine(line) for line in list_lines]
    list_recipes = RecipeList.query.filter_by(complist=list).all()

    # reverse list and remove "additional ingredients" recipe
    list_recipes.reverse()
    list_recipes = [recipe for recipe in list_recipes if recipe.name != "Additional Ingredients"]

    rendered = render_template('print_template.html',
                               list=list,
                               lines=list_lines,
                               list_recipes=list_recipes,
                               print_checked=request.form.get("export-pdf-show_checked", "n"),
                               print_recipes=request.form.get("export-pdf-show_recipes", "n"),
                               print_lines=request.form.get("export-pdf-show_lines", "n"))

    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'

    return response