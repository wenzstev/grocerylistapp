from flask import Flask
import spacy
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from grocerylistapp.config import Config

db = SQLAlchemy()
mail = Mail()
nlp = spacy.load('ingredient_test')


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    mail.init_app(app)

    from grocerylistapp.main.routes import main
    from grocerylistapp.checklist.routes import checklist
    from grocerylistapp.line.routes import line
    from grocerylistapp.recipe.routes import recipe
    app.register_blueprint(main)
    app.register_blueprint(checklist)
    app.register_blueprint(line)
    app.register_blueprint(recipe)

    return app
