from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import current_user

from grocerylistapp import db

from grocerylistapp.models import RecipeList, RawLine, CompiledList, CleanedLine
from grocerylistapp.forms import CustomRecipeForm
from grocerylistapp.constructors import create_recipe_from_text, LineToPass
from grocerylistapp.nlp import extract_ingredients

from grocerylistapp.recipe.forms import RecipeCleanForm

recipe = Blueprint('recipe', __name__)


@recipe.route('/list/<string:list_name>/clean_recipe/<string:new_recipe>', methods=['GET', 'POST'])
def clean_recipe(list_name, new_recipe):
    rlist = RecipeList.query.filter_by(hex_name=new_recipe).first_or_404()
    rlist_lines = RawLine.query.filter_by(rlist=rlist).all()

    print(rlist.recipe_url)

    if not rlist_lines:  # we failed to extract any lines from the recipe, redirect
        form = CustomRecipeForm()
        if form.validate_on_submit():
            print('checking recipe')
            recipe = create_recipe_from_text("Untitled Recipe", form.recipe_lines.data)
            recipe.name = form.name.data
            recipe.recipe_url = rlist.recipe_url
            db.session.commit()
            db.session.delete(rlist)
            return redirect(url_for('recipe.clean_recipe', list_name=list_name, new_recipe=recipe.hex_name))

        form.name.data = rlist.name
        flash('Error: Could not parse recipe lines. Please paste or type recipe lines below: ', 'danger')
        return render_template('custom_add_recipe.html', form=form, rlist=rlist)

    form = RecipeCleanForm(request.form)
    if form.validate_on_submit():
        print(form.name.data)

        current_list = CompiledList.query.filter_by(hex_name=list_name).first_or_404()
        current_list_lines = CleanedLine.query.filter_by(list=current_list).all()

        current_list_length = len(current_list_lines)  # get the length of the current list

        ingredient_dict = {line.ingredient: line for line in current_list_lines}  # dictionary to make checking if line exists easier

        # add recipe to the list
        rlist.compiled_list = current_list.id   # won't matter if recipe is already on the list
        rlist.name = form.name.data
        db.session.commit()

        for line in rlist_lines:
            amount, measurement, ingredient = extract_ingredients(line.text_to_colors)
            if ingredient != '':  # only create cleaned line if we found an ingredient
                if ingredient not in ingredient_dict:

                    # check if rawline already has a cleanedline
                    if line.cline_id:
                        # remove the old line
                        cleaned_line_to_delete = CleanedLine.query.filter_by(id=line.cline_id).first()
                        raw_line_check_list = RawLine.query.filter_by(cleaned_line=cleaned_line_to_delete).all()
                        if len(raw_line_check_list) == 1:  # check if other RawLines link to this CompiledLine
                            db.session.delete(cleaned_line_to_delete)
                            db.session.commit()

                    cleaned_line = CleanedLine(amount=amount,
                                               measurement=measurement,
                                               ingredient=ingredient,
                                               list=current_list,
                                               index_in_list=current_list_length)
                    current_list_length += 1  # add one to get the new length of the list

                    db.session.add(cleaned_line)
                    db.session.commit()

                    line.cleaned_line = cleaned_line
                    ingredient_dict[ingredient] = cleaned_line
                    db.session.commit()
                else:
                    line.cleaned_line = ingredient_dict[ingredient]

        return redirect(url_for('checklist.compiled_list', hex_name=current_list.hex_name))

    form.name.data = rlist.name

    rlist_lines = [LineToPass(line) for line in rlist_lines]

    grocery_list = CompiledList.query.filter_by(user_id=current_user.id)

    return render_template('add_recipe.html', title="Adding Recipe", rlist=rlist, rlist_lines=rlist_lines, form=form)
