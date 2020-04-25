import requests

from urllib.parse import urlparse

from bs4 import BeautifulSoup

# repeated attributes for sites using WordPress Recipe maker
wprm_scrapers = {
    "title": ("h2", "class", "wprm-recipe-name"),
    "lines": ("li", "class", "wprm-recipe-ingredient")
}

# dictionary that stores the specifications for scraping various websites
ingredient_parsers = {
    "www.allrecipes.com": {
        "title": ("h1", "id", "recipe-main-content"),
        "lines": ("span", "class", "recipe-ingred_txt")
    },
    "www.foodnetwork.com": {
        "title": ("span", "class", "o-AssetTitle__a-HeadlineText"),
        "lines": ("p", "class", "o-Ingredients__a-Ingredient")
    },
    "www.food.com": {
        "title": ("div", "class", "recipe-title"),
        "lines": ("div", "class", "recipe-ingredients__ingredient")
    },
    "www.yummly.com": {
        "title": ("h1", "class", "recipe-title"),
        "lines": ("li", "class", "IngredientLine")
    },
    "www.epicurious.com": {
        "title": ("h1", "itemprop", "name"),
        "lines": ("li", "class", "ingredient")
    },
    "www.seriouseats.com": {
        "title": ("h1", "class", "recipe-title"),
        "lines": ("li", "class", "ingredient")
    },
    "smittenkitchen.com": {
        "title": ("h3", "class", "jetpack-recipe-title"),
        "lines": ("li", "class", "ingredient")
    },
    "www.simplyrecipes.com": {
        "title": ("h1", "class", "entry-title"),
        "lines": ("li", "class", "ingredient")
    },
    "minimalistbaker.com": wprm_scrapers,
    "www.budgetbytes.com": wprm_scrapers

}


# these are websites that need a more sophisticated way to scrape the recipe
def get_recipe_food52(soup):
    print("getting from food52")
    ingredient_div = soup.find("div", {"class": "recipe__list"})
    ingredient_list = ingredient_div.find("ul")
    ingredient_items = ingredient_list.find_all("li")

    ingredient_lines = []

    for line in ingredient_items:
        line = line.text.replace("\n", " ")
        s_line = line.split()
        line = " ".join(s_line)
        ingredient_lines.append(line)

    try:
        title = soup.find("h1", {"class": "recipe__title"}).get_text()
    except AttributeError:
        title = soup.title.get_text()

    return {
        "title": title,
        "recipe_lines": ingredient_lines
    }


# function for scraping websites that use the TastyRecipes plugin
def get_recipe_tastyrecipes(soup):
    ingredient_div = soup.find("div", {"class": "tasty-recipe-ingredients"})
    ingredient_lines = ingredient_div.find_all("li")
    recipe_lines = []
    for line in ingredient_lines:
        recipe_lines.append(line.text)
        print(line.text)

    recipe_title_div = soup.find("div", {"class": "tasty-recipes"})
    recipe_title = recipe_title_div.find("h2")

    return {
        "title": recipe_title.text,
        "recipe_lines": recipe_lines
    }


def get_recipe_sallysbakingaddiction(soup):
    # 403 error
    pass


ingredient_functions = {
    "food52.com": get_recipe_food52,
    "cookieandkate.com": get_recipe_tastyrecipes,
}

def get_recipe_info(url):
    res = requests.get(url)
    if res.status_code != 200:
        # didn't get the recipe properly
        return {"error": res.status_code}

    soup = BeautifulSoup(res.text)

    o = urlparse(url)

    print('url is from ', o.netloc)

    parsing_information = ingredient_parsers.get(o.netloc, "")

    if parsing_information:
        print("found for ", parsing_information)
        # get information for the title
        component, attribute, name = parsing_information["title"]
        print(component, attribute, name)

        try:
            recipe_title = soup.find(component, {attribute: name}).get_text()
        except AttributeError:
            recipe_title = soup.title.get_text()  # we get some kind of name if we can't parse the actual recipe

        # get information for the lines
        component, attribute, name = parsing_information["lines"]
        ingredients = soup.find_all(component, {attribute: name})
        ingredient_lines = [line.get_text() for line in ingredients]

    elif o.netloc in ingredient_functions:
        print("found in ingredient functions")
        return ingredient_functions[o.netloc](soup)

    else:
        # the user's recipe isn't recognized
        recipe_title = soup.title.get_text()
        ingredient_lines = []

    return {
        "title": recipe_title,
        "recipe_lines": ingredient_lines
    }


def get_recipe_allrecipes(soup):
    ingredient_classes = soup.find_all("span", class_="recipe-ingred_txt")
    ingredient_lines = [line.get_text() for line in ingredient_classes]

    recipe_title = soup.find("h1", {"id": "recipe-main-content"}).get_text()

    print(recipe_title)

    return {
        'title': recipe_title,
        'recipe_lines': ingredient_lines
    }


def get_recipe_foodnetwork(soup):
    ingredients = soup.find_all("p", class_="o-Ingredients__a-Ingredient")
    ingredient_lines = [line.get_text() for line in ingredients]

    recipe_title = soup.find("span", {"class": "o-AssetTitle__a-HeadlineText"}).get_text()

    return {
        'title': recipe_title,
        'recipe_lines': ingredient_lines
    }


def get_recipe_foodcom(soup):
    ingredients = soup.find_all("div", class_="recipe-ingredients__ingredient")
    ingredient_lines = [line.get_text() for line in ingredients]

    recipe_title = soup.find("div", {"class": "recipe-title"}).get_text()



    return {
        'title': recipe_title,
        'recipe_lines': ingredient_lines
    }


def get_recipe_thekitchn(soup):
    ingredients = soup.find_all("li", class_="Recipe__ingredient")
    ingredient_lines = [line.get_text() for line in ingredients]

    recipe_title = soup.find("h2", {"class": "Recipe__title"}).get_text()

    print(recipe_title)

    return {
        'title': recipe_title,
        'recipe_lines': ingredient_lines
    }


def get_recipe_yummly(soup):
    ingredients = soup.find_all("li", {"class": "IngredientLine"})
    ingredient_lines = [line.get_text() for line in ingredients]

    recipe_title = soup.find("h1", {"class": "recipe-title"}).get_text()

    return {
        'title': recipe_title,
        'recipe_lines': ingredient_lines
    }




def get_title(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')

    return soup.title.string