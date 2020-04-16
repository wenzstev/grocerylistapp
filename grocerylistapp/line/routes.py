import json

from flask import Blueprint, request, jsonify, redirect, url_for

from grocerylistapp import db
from grocerylistapp.models import RawLine, RecipeList, CleanedLine, CompiledList

from grocerylistapp.constructors import color_entities_in_line
from grocerylistapp.nlp import extract_ingredients

line = Blueprint('line', __name__)


@line.route('/line/get_colors', methods=['GET', 'POST'])
def get_colors():
    cur_line = RawLine.query.filter_by(hex_id=request.form.get('hex_id', '', str)).first_or_404()

    print(cur_line.text_to_colors)

    return {'hex_id': cur_line.hex_id,
            'parsed_line': json.loads(cur_line.text_to_colors)}


@line.route('/line/set_color', methods=['GET', 'POST'])
def set_color():

    print(request.form)

    # get ingredients before changing so that we can compare (performance hit?)
    amount, measurement, old_ingredients = extract_ingredients(cur_line.text_to_colors)

    cur_line = RawLine.query.filter_by(hex_id=request.form.get('rawline_id', '', str)).first_or_404()
    new_colors = request.form.get('text_to_colors', '', type=str)
    cur_line.text_to_colors = new_colors
    db.session.commit()
    print(cur_line.text_to_colors)

    # check if we have a cleaned line as well
    cline_to_change = CleanedLine.query.filter_by(hex_id=request.form.get('cleanedline_id')).first()
    if cline_to_change:
        # recalculate the line
        amount, measurement, ingredients = extract_ingredients(cur_line.text_to_colors)

        # check if there are the same number of ingredients
        if len(ingredients) == len(old_ingredients):
            # we still have the same number of ingredients
            cline_to_change.ingredient = ingredients[cline_to_change.rawline_index]

        elif len(ingredients) < len(old_ingredients):
            # we have combined ingredients

            cline_index = cline_to_change.rawline_index
            if cline_index == 0:
                #beginning of list, combination can only be right
                cline_to_change.ingredient = ingredients[cline_to_change.rawline_index]

                pass

            elif cline_index > len(ingredients):
                # end of list, combination can only be left
                pass




            # get all clines

            # need to figure out what was combined

            # remove rawline from other cline

            pass
        elif len(ingredients) > len(old_ingredients):
            # we have split ingredients
            pass

        # change the ingredient to the new value on cur_line




    return jsonify(new_colors)


@line.route('/line/parse_line', methods=['GET', 'POST'])
def parse_line():
    new_line = request.form.get('line_text', '', type=str)
    print(new_line)
    parsed_line = color_entities_in_line(new_line)
    print(parsed_line)

    cur_list_hex = request.form.get('compiled_list', '', type=str)
    cur_list = CompiledList.query.filter_by(hex_name=cur_list_hex).first_or_404()

    user_ingredient_recipe = RecipeList.query.filter_by(complist=cur_list, name="Additional Ingredients").first_or_404()
    user_ingredient_lines = RawLine.query.filter_by(rlist=user_ingredient_recipe).all()

    new_raw_line = RawLine(id_in_list=len(user_ingredient_lines)+1,
                           rlist=user_ingredient_recipe,
                           full_text=new_line,
                           text_to_colors=parsed_line)

    db.session.add(new_raw_line)
    db.session.commit()

    # get the index for the new line
    cur_list_num = len(CleanedLine.query.filter_by(list=cur_list).all())
    print('index will be ', cur_list_num)

    amount, measurement, ingredient = extract_ingredients(new_raw_line.text_to_colors)

    new_cleaned_line = CleanedLine(amount=amount,
                                   measurement=measurement,
                                   ingredient=ingredient,
                                   list=cur_list,
                                   index_in_list=cur_list_num)
    db.session.add(new_cleaned_line)
    new_raw_line.cleaned_line = new_cleaned_line
    db.session.commit()

    print(json.loads(parsed_line))

    return {'line_id': new_raw_line.id,
            'parsed_line': json.loads(parsed_line)}  # have to load it to make sure it's formatted properly for client


@line.route('/line/checked', methods=['POST'])
def toggle_line_check():
    print(request.form.get('line'))
    line_to_toggle = CleanedLine.query.filter_by(hex_id=request.form.get('line', '', type=str)).first_or_404()
    line_to_toggle.checked = not line_to_toggle.checked
    db.session.commit()
    return jsonify(isActive=line_to_toggle.checked,
                   line=line_to_toggle.hex_id)


@line.route('/line/delete', methods=['POST'])
def delete_line():
    print(request.form.get('line'))
    line_to_delete = CleanedLine.query.filter_by(hex_id=request.form.get('line', '', type=str)).first_or_404()
    db.session.delete(line_to_delete)
    db.session.commit()
    return jsonify(line=request.form.get('line'))


