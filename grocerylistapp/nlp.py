import json
from fractions import Fraction
from grocerylistapp import nlp

# at the moment, only using INGREDIENT, so the other classes are assigned a base class as well
line_colors = {
    "INGREDIENT": "btn-ingredient",
    "CARDINAL": "btn-base",
    "QUANTITY": "btn-base",
    "O": "btn-base"
}


# method that takes in json data from line colors and returns tuple of (amount, measurement, ingredient)
def extract_ingredients(color_string,
                        ingredient_color="text-success",
                        cardinal_color="text-warning",
                        quantity_color="text-primary"):
    ingredients = []    # list of ingredients in the line
    measurement = ''    # not currently used
    amount = 0          # not currently used
    color_dict = json.loads(color_string)
    in_ingredient = False
    current_ingredient = ''
    for word, color in color_dict:
        if color == line_colors["INGREDIENT"]:
            in_ingredient = True
            current_ingredient += word + ' '
        elif in_ingredient:
            in_ingredient = False
            ingredients.append(current_ingredient)
            current_ingredient = ''
    if current_ingredient:
        ingredients.append(current_ingredient)

    return amount, measurement, ingredients


def color_entities_in_line(line, line_colors=line_colors):
    color_tuples = []   # list of tuples of token and the color
    doc = nlp(line)
    for token in doc:
        if token.ent_iob_ == "O":   # if the token is outside an entity
            color_tuples.append((token.text, line_colors["O"]))
        else:
            color_tuples.append((token.text, line_colors[token.ent_type_]))
    return json.dumps(color_tuples)
