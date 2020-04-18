from flask import Blueprint, redirect, url_for, render_template, request, flash, jsonify
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

    if request.method == "POST":  # we submitted the changes, time to create the cleaned lines
        current_list = CompiledList.query.filter_by(hex_name=list_name).first_or_404()
        current_list_lines = CleanedLine.query.filter_by(list=current_list).all()

        current_list_length = len(current_list_lines)  # get the length of the current list

        ingredient_dict = {line.ingredient: line for line in current_list_lines}  # dictionary to make checking if line exists easier

        # add recipe to the list
        rlist.compiled_list = current_list.id   # won't matter if recipe is already on the list
        db.session.commit()

        for line in rlist_lines:
            print(line.text_to_colors)
            amount, measurement, ingredient_tuples = extract_ingredients(line.text_to_colors)
            for index, ingredient_tuples in enumerate(ingredient_tuples):
                print(index, ingredient_tuples)
                ingredient, color = ingredient_tuples
                if ingredient not in ingredient_dict:


                    cleaned_line = CleanedLine(amount=amount,
                                               measurement=measurement,
                                               ingredient=ingredient,
                                               list=current_list,
                                               index_in_list=current_list_length,
                                               rawline_index=index,
                                               ingredient_color=color)
                    current_list_length += 1  # add one to get the new length of the list

                    db.session.add(cleaned_line)
                    db.session.commit()

                    line.cleaned_lines.append(cleaned_line)
                    ingredient_dict[ingredient] = cleaned_line
                    db.session.commit()
                else:
                    line.cleaned_lines.append(ingredient_dict[ingredient])

        return redirect(url_for('checklist.compiled_list', hex_name=current_list.hex_name))

    rlist_lines = [LineToPass(line) for line in rlist_lines]

    grocery_lists = CompiledList.query.filter_by(user_id=current_user.id)

    return render_template('add_recipe.html', title="Adding Recipe", rlist=rlist, rlist_lines=rlist_lines, grocery_lists=grocery_lists)



@recipe.route('/recipe/rename', methods=['POST'])
def rename_recipe():
    recipe_to_rename = RecipeList.query.filter_by(hex_name=request.form.get('recipe_id', '', type=str)).first_or_404()
    recipe_to_rename.name = request.form.get('name', recipe.name, type=str)
    db.session.commit()

    return jsonify(new_name=recipe_to_rename.name)
