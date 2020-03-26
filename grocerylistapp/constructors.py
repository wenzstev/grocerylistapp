import json, secrets, random, requests

from bs4 import BeautifulSoup

from grocerylistapp import db
from grocerylistapp.models import RecipeList, CompiledList, RawLine, CleanedLine
from grocerylistapp.nlp import color_entities_in_line


# class that takes the db Line object and turns it into a python class to pass to the template
class LineToPass:
    def __init__(self, list_line):
        self.full_text = list_line.full_text
        self.text_to_colors = json.loads(list_line.text_to_colors)
        self.id_in_list = list_line.id_in_list
        self.list_id = list_line.list_id  # the ID of the RECIPELIST FIXME: these names need changing
        self.recipe = RecipeList.query.filter_by(id=self.list_id).first()


# class that takes the db CleanedLine object and turns it into a python class to pass to template
class CompiledIngredientLine:
    def __init__(self, cleaned_line):
        self.hex_id = cleaned_line.hex_id

        self.ingredient = cleaned_line.ingredient
        self.amount = cleaned_line.amount
        self.measurement = cleaned_line.measurement

        self.ingredient_id = cleaned_line.ingredient.strip().replace(" ", "-")  # ingredient id for use in html

        self.checked = ""
        if cleaned_line.checked:
            self.checked = " checked"

        # get list of all raw lines that make up the cleaned line
        self.raw_lines = RawLine.query.filter_by(cleaned_line=cleaned_line).all()

        self.raw_lines = [LineToPass(line) for line in self.raw_lines]

        self.color_dots = set()
        for raw_line in self.raw_lines:
            recipe = RecipeList.query.filter_by(id=raw_line.list_id).first()
            if recipe:
                self.color_dots.add(recipe.hex_color)


# creates a new recipe
def create_recipe(title):
    random_hex = secrets.token_urlsafe(8)
    r = lambda: random.randint(0, 255)
    hex_color = ('#%02X%02X%02X' % (r(), r(), r()))
    rlist = RecipeList(hex_name=random_hex, hex_color=hex_color, name=title) # FIXME: make recipe_url optional
    db.session.add(rlist)
    db.session.commit()
    return rlist


def create_recipe_from_url(url):
    rlist = create_recipe(get_title(url))
    rlist.recipe_url = url
    recipe_lines = get_recipe_lines(url)  # TODO: possibly refactor code so that get_recipe_lines is here too
    for num, line in enumerate(recipe_lines):
        recipe_colors = color_entities_in_line(line)
        recipe_line = RawLine(full_text=line, rlist=rlist, id_in_list=num, text_to_colors=recipe_colors)
        db.session.add(recipe_line)
    db.session.commit()

    return rlist   # return the new recipe for use in the route


def create_recipe_from_text(title, recipe_text):
    print('creating recipe from text')
    recipe = create_recipe(title)
    recipe_lines = recipe_text.splitlines()

    def elim_blanks(line):  # function to remove blank lines and spaces from list
        if not line or line.isspace():
            return False
        else:
            return True

    recipe_lines = filter(elim_blanks, recipe_lines)

    print(recipe_lines)

    for num, line in enumerate(recipe_lines):  # FIXME: this code is the same as in utils.url_to_recipe
        print(line)
        recipe_colors = color_entities_in_line(line)
        recipe_line = RawLine(full_text=line, rlist=recipe, id_in_list=num, text_to_colors=recipe_colors)
        db.session.add(recipe_line)
    db.session.commit()

    return recipe


def get_recipe_lines(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')

    ingredient_classes = soup.find_all("span", class_="recipe-ingred_txt added")
    ingredient_lines = [line.get_text() for line in ingredient_classes]

    return ingredient_lines


def get_title(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')

    return soup.title.string