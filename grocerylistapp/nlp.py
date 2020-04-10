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
    ingredient = ''
    measurement = ''
    amount = 0
    color_dict = json.loads(color_string)
    for word, color in color_dict:
        print(word, color)
        if color == line_colors["INGREDIENT"]:
            ingredient += word + ' '
        elif color == line_colors["CARDINAL"]:
            amount = float(sum(Fraction(s) for s in word.split()))  # treat the string as a fraction and sum
        elif color == line_colors["QUANTITY"]:
            try:
                amount = float(sum(Fraction(s) for s in word.split()))  # see if the word is an amount
            except ValueError:  # if it's not an amount
                measurement += word + ' '

    return amount, measurement, ingredient


def color_entities_in_line(line, line_colors=line_colors):
    color_tuples = []   # list of tuples of token and the color
    doc = nlp(line)
    for token in doc:
        if token.ent_iob_ == "O":   # if the token is outside an entity
            color_tuples.append((token.text, line_colors["O"]))
        else:
            color_tuples.append((token.text, line_colors[token.ent_type_]))
    return json.dumps(color_tuples)
