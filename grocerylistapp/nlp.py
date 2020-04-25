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

line_ingredients = ["ing-1", "ing-2", "ing-3"]


# method that takes in json data from line colors and returns tuple of (amount, measurement, ingredient)
def extract_ingredients(color_string,
                        ingredient_color="text-success",
                        cardinal_color="text-warning",
                        quantity_color="text-primary"):
    ingredients = []    # list of ingredients in the line
    measurement = ''    # not currently used
    amount = 0          # not currently used
    color_dict = json.loads(color_string)
    print("color dict is ")
    print(color_dict)
    current_ingredient = ''
    ingredient_class = ''
    for word, classes in color_dict:
        colors = classes.split()
        print(colors)
        # check the length of the colors because otherwise removing a button from an ingredient will throw an error
        if line_colors["INGREDIENT"] in colors and len(colors) > 1:  # we're in an ingredient
            print("found an ingredient: ", word)
            if ingredient_class == colors[1]: # we're already in the ingredient
                current_ingredient += word + ' '
            else:   # new ingredient, check if coming from adjacent or not
                if not ingredient_class:
                    # we're starting an ingredient
                    current_ingredient += word + ' '
                    ingredient_class = colors[1]
                else:
                    # new, adjacent ingredient
                    print("appending ingredient: ", current_ingredient)
                    ingredients.append((current_ingredient.strip(), ingredient_class))
                    current_ingredient = word + ' '
                    ingredient_class = colors[1]
        else:  # not in ingredient
            print("length of current is ", len(current_ingredient))
            if len(current_ingredient) > 0:
                # we ended an ingredient, need to add it
                print("appending ingredient: ", current_ingredient)
                ingredients.append((current_ingredient.strip(), ingredient_class))
                current_ingredient = ''
                ingredient_class = ''  # reset the class

    if current_ingredient:  # end of line
        print("end of line")
        print("appending ingredient: ", current_ingredient)

        ingredients.append((current_ingredient.strip(), ingredient_class))

    print(ingredients)

    return amount, measurement, ingredients



def color_entities_in_line(line, line_colors=line_colors):
    cur_ingredient = -1
    in_ingredient = False
    color_tuples = []   # list of tuples of token and the color
    doc = nlp(line)
    for token in doc:
        print(token.ent_iob_)
        if token.ent_type_ == "INGREDIENT":
            if token.ent_iob_ == "B":
                cur_ingredient += 1 if cur_ingredient < 2 else 0
            color_tuples.append((token.text,  "btn-ingredient " + line_ingredients[cur_ingredient]))
        else:
            color_tuples.append((token.text, line_colors["O"]))


    return json.dumps(color_tuples)
