import json

from flask import Blueprint, request, jsonify, redirect, url_for, render_template

from grocerylistapp import db
from grocerylistapp.models import RawLine, RecipeList, CleanedLine, CompiledList

from grocerylistapp.constructors import CompiledIngredientLine
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
    cur_line = RawLine.query.filter_by(hex_id=request.form.get('rawline_id', '', str)).first_or_404()

    new_colors = request.form.get('text_to_colors', '', type=str)
    cur_line.text_to_colors = new_colors
    db.session.commit()

    print(cur_line.text_to_colors)

    # check if we have a cleaned line as well
    print(request.form.get('cleanedline_id'))
    cline_to_change = CleanedLine.query.filter_by(hex_id=request.form.get('cleanedline_id')).first()
    clines_to_change = cur_line.cleaned_lines
    # if we have cleaned lines to change
    if clines_to_change:
        payload = {"change": []}
        current_list = CompiledList.query.filter_by(hex_name=request.form.get("list_id", "")).first_or_404()
        amount, measurement, ingredient_tuples = extract_ingredients(cur_line.text_to_colors)

        for ingredient_tuple in ingredient_tuples:
            ingredient, color = ingredient_tuple
            print(ingredient, color)
            cline_for_ingredient = CleanedLine.query.filter_by(list=current_list, ingredient=ingredient).first()
            # check if cline exists and if there is not an association between it and the rawline (for multiple ingredients)
            if cline_for_ingredient:
                print("cline found: ", cline_for_ingredient)
                if cline_for_ingredient not in cur_line.cleaned_lines:
                    print("moving to existing cline")
                    # there is an existing cleaned line with this ingredient
                    cur_line.cleaned_lines.append(cline_for_ingredient)
                    print(cur_line.cleaned_lines)
                    if cline_to_change.ingredient_color == color:
                        cur_line.cleaned_lines.remove(cline_to_change)
                    db.session.commit()
                    payload["type"] = "moved"
                    payload["change"].append((cur_line.hex_id, cline_for_ingredient.hex_id))
            elif len(cline_to_change.raw_lines.all()) == 1 and cline_to_change.ingredient_color == color:
                print("changing existing cline")
                # this is the only rawline associated with this line, so it's okay to just change it
                cline_to_change.ingredient = ingredient
                db.session.commit()
                payload["type"] = "changed"
                payload["change"].append((cline_to_change.hex_id, ingredient))
            elif cline_to_change.ingredient_color == color:  # we need to make sure we don't accidentally create additional lines
                # no existing cleaned line, and there are additional lines pointing to this cleaned line, so we make a new one
                print("creating new cline")
                print(ingredient, 0, 0, current_list, 0, color, len(current_list.lines))
                new_cline = CleanedLine(ingredient=ingredient,
                                        amount=0,
                                        measurement="0",
                                        rawline_index=0,    # because there's only the one ingredient on this line
                                        ingredient_color=color,
                                        comp_list=current_list.id,
                                        index_in_list=len(current_list.lines))
                db.session.add(new_cline)
                db.session.commit()
                cur_line.cleaned_lines.append(new_cline)
                if cline_to_change.ingredient_color == color:
                    cur_line.cleaned_lines.remove(cline_to_change)
                payload["type"] = "create"
                payload["change"].append((cur_line.hex_id, new_cline.hex_id))

            if len(cline_to_change.raw_lines.all()) == 0:
                # there are no longer any recipe lines pointing to this ingredient, delete it
                print("deleting old line")
                payload["delete"] = cline_to_change.hex_id
                db.session.delete(cline_to_change)


        print("preparing to commit")
        db.session.commit()
        print("committed")

        changed_lines = {cline.hex_id: cline.ingredient for cline in clines_to_change}


        return json.dumps(payload)

    return jsonify(new_colors)


@line.route('/line/parse_line', methods=['GET', 'POST'])
def parse_line():
    new_line = request.form.get('line_text', '', type=str)
    print(new_line)

    text_to_colors = []

    # create text_to_colors
    for word in new_line.split():
        text_to_colors.append((word, "btn-ingredient ing-1"))

    text_to_colors = json.dumps(text_to_colors)

    print(text_to_colors)

    # get the grocery list
    cur_list_hex = request.form.get('compiled_list', '', type=str)
    cur_list = CompiledList.query.filter_by(hex_name=cur_list_hex).first_or_404()

    # get the additional ingredient recipe
    additional_ingredient_recipe = RecipeList.query.filter_by(complist=cur_list, name="Additional Ingredients").first_or_404()
    additional_ingredient_lines = RawLine.query.filter_by(rlist=additional_ingredient_recipe).all()

    new_raw_line = RawLine(rlist=additional_ingredient_recipe,
                           full_text=new_line,
                           text_to_colors=text_to_colors)

    db.session.add(new_raw_line)
    db.session.commit()

    # get the index for the new line
    cur_list_num = len(CleanedLine.query.filter_by(list=cur_list).all())
    print('index will be ', cur_list_num)

    # check if we entered a duplicate ingredient
    cline_to_render = CleanedLine.query.filter_by(ingredient=new_line, list=cur_list).first()
    print(cline_to_render)
    if cline_to_render:
        print("cline exists")
        new_raw_line.cleaned_lines.append(cline_to_render)
    else:
        cline_to_render = CleanedLine(amount=0,
                                       measurement=0,
                                       ingredient=new_line,
                                       list=cur_list,
                                       index_in_list=cur_list_num,
                                       rawline_index=0,
                                       ingredient_color='ing-1')
        db.session.add(cline_to_render)
        new_raw_line.cleaned_lines.append(cline_to_render)
    db.session.commit()

    return render_template("list-snippit.html", line=CompiledIngredientLine(cline_to_render))


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


@line.route('/line/build', methods=['POST'])
def build_line():
    print(request.form.get('line'))
    line_to_build = CleanedLine.query.filter_by(hex_id=request.form.get('line')).first_or_404()

    return render_template("list-snippit.html", line=CompiledIngredientLine(line_to_build))
