import json

from flask import Blueprint, request, jsonify, redirect, url_for

from grocerylistapp import db
from grocerylistapp.models import RawLine, RecipeList, CleanedLine, CompiledList

from grocerylistapp.constructors import color_entities_in_line
from grocerylistapp.nlp import extract_ingredients

line = Blueprint('line', __name__)


@line.route('/line/get_colors', methods=['GET', 'POST'])
def get_colors():
    # check if finding by line id or recipe hex
    line_id = request.form.get('line_id', -1, int)
    print(line_id)
    if line_id > 0:  # if we have a line id
        cur_line = RawLine.query.filter_by(line_id).first_or_404()
    else:  # we're finding it from a recipe hex
        recipe_hex = request.form.get('hex_name', '', str)
        recipe_line = request.form.get('recipe_line', -1, int)
        recipe = RecipeList.query.filter_by(hex_name=recipe_hex).first_or_404()
        cur_line = RawLine.query.filter_by(rlist=recipe, id_in_list=recipe_line).first_or_404()

    return {'line_id': cur_line.id,
            'parsed_line': json.loads(cur_line.text_to_colors)}


@line.route('/line/set_color', methods=['GET', 'POST'])
def set_color():
    # check if we're finding by line id or by hex name
    # TODO: refactor code so that this section and the identical section in get_colors are in one function
    line_id = request.form.get('line_id', -1, int)
    if line_id > 0:  # if we have a line id
        print('going by id')
        cur_line = RawLine.query.filter_by(id=line_id).first_or_404()
    else:  # we're finding it from a recipe hex
        print('going by hex')
        recipe_hex = request.form.get('hex_name', '', str)
        recipe_line = request.form.get('recipe_line', -1, int)
        print(recipe_hex, recipe_line)
        recipe = RecipeList.query.filter_by(hex_name=recipe_hex).first_or_404()
        cur_line = RawLine.query.filter_by(rlist=recipe, id_in_list=recipe_line).first_or_404()
        print(cur_line)

    new_colors = request.form.get('text_to_colors', '', type=str)
    print(request.form.get('text_to_colors'))
    print(request.is_json)
    print('new colors', new_colors)

    cur_line.text_to_colors = new_colors
    db.session.commit()
    #  check if there is a cleaned line for this raw line yet
    if cur_line.cline_id:
        amount, measurement, ingredient = extract_ingredients(cur_line.text_to_colors)
        print('getting cleaned line:', cur_line.cline_id)
        cur_cleaned_line = CleanedLine.query.filter_by(id=cur_line.cline_id).first_or_404()
        # check if there is more than one raw line that points to this cleaned line
        # TODO: modify cleaned line code to check if there is more than one raw line (and split them if necessary)
        print(cur_cleaned_line)
        cur_cleaned_line.amount = amount
        cur_cleaned_line.measurement = measurement
        cur_cleaned_line.ingredient = ingredient

        db.session.commit()

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


