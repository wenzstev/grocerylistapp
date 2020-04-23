import json, secrets, random, requests


from grocerylistapp import db
from grocerylistapp.models import RecipeList, CompiledList, RawLine, CleanedLine, User
from grocerylistapp.nlp import color_entities_in_line
from grocerylistapp.scraper import get_title, get_recipe_info


# class that takes the db Line object and turns it into a python class to pass to the template
class LineToPass:
    def __init__(self, list_line):
        self.full_text = list_line.full_text
        self.text_to_colors = json.loads(list_line.text_to_colors)
        self.hex_id = list_line.hex_id
        self.list_id = list_line.list_id  # the ID of the RECIPELIST FIXME: these names need changing
        self.recipe = RecipeList.query.filter_by(id=self.list_id).first()


# class that takes the db CleanedLine object and turns it into a python class to pass to template
class CompiledIngredientLine:
    def __init__(self, cleaned_line):
        self.hex_id = cleaned_line.hex_id

        self.ingredient = cleaned_line.ingredient
        self.amount = cleaned_line.amount
        self.measurement = cleaned_line.measurement

        ingredient_id = cleaned_line.ingredient.replace(",", "").replace("-", "") # ingredient id for use in html
        ingredient_id = ingredient_id.split()
        ingredient_id = '-'.join(ingredient_id)
        self.ingredient_id = ingredient_id

        self.checked = ""
        if cleaned_line.checked:
            self.checked = " checked"

        # get list of all raw lines that make up the cleaned line
        self.raw_lines = cleaned_line.raw_lines

        self.raw_lines = [LineToPass(line) for line in self.raw_lines]

        self.ingredient_color = cleaned_line.ingredient_color

        self.color_dots = set()
        for raw_line in self.raw_lines:
            recipe = RecipeList.query.filter_by(id=raw_line.list_id).first()
            if recipe:
                self.color_dots.add(recipe.hex_color)



class ChecklistCard:
    def __init__(self, checklist, num_samples):
        self.name = checklist.name
        self.hex_name = checklist.hex_name
        self.lines = CleanedLine.query.filter_by(list=checklist).all()
        self.recipes = RecipeList.query.filter(RecipeList.complist == checklist,
                                               RecipeList.name != "Additional Ingredients").all()

        self.sample_lines = self.lines[:num_samples]
        self.sample_recipes = self.recipes[:num_samples]

        self.leftover_recipes = len(self.recipes) - len(self.sample_recipes)
        self.date_created = checklist.date_created

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
    recipe_info = get_recipe_info(url)  # TODO: possibly refactor code so that get_recipe_lines is here too


    rlist = create_recipe(recipe_info['title'])
    rlist.recipe_url = url
    for num, line in enumerate(recipe_info['recipe_lines']):
        recipe_colors = color_entities_in_line(line)
        recipe_line = RawLine(full_text=line, rlist=rlist, text_to_colors=recipe_colors)
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
        split_line = line.split()
        rejoined_line = ' '.join(split_line)  # do this to eliminate double spaces
        print(rejoined_line)
        recipe_colors = color_entities_in_line(rejoined_line)
        recipe_line = RawLine(full_text=rejoined_line, rlist=recipe, text_to_colors=recipe_colors)
        db.session.add(recipe_line)
    db.session.commit()

    return recipe


def create_guest_user():
    guest_username = secrets.token_urlsafe(8)
    guest_password = secrets.token_urlsafe(8)
    guest_email = secrets.token_urlsafe(8)

    guest_user = User(username=guest_username, password=guest_password, email=guest_email, temporary=True)
    db.session.add(guest_user)
    db.session.commit()
    return guest_user
