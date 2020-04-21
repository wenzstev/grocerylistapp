import requests

from urllib.parse import urlparse

from bs4 import BeautifulSoup

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
    "www.thekitchn.com": {
        "title": ("h2", "class", "Recipe__title"),
        "lines": ("li", "class", "Recipe__ingredient")
    },
    "www.yummly.com": {
        "title": ("h1", "class", "recipe-title"),
        "lines": ("li", "class", "IngredientLine")
    }
}

def get_recipe_info(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text)

    o = urlparse(url)

    print('url is from ', o.netloc)

    parsing_information = ingredient_parsers.get(o.netloc, "")

    if parsing_information:
        print("found for ", parsing_information)
        # get information for the title
        component, attribute, name = parsing_information["title"]
        recipe_title = soup.find(component, {attribute: name}).get_text()

        # get information for the lines
        component, attribute, name = parsing_information["lines"]
        ingredients = soup.find_all(component, {attribute: name})
        ingredient_lines = [line.get_text() for line in ingredients]

        return {
            "title": recipe_title,
            "recipe_lines": ingredient_lines
        }

    return None


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