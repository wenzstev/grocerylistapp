from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField


class AddLineForm(FlaskForm):
    recipe_line = StringField("Type an Ingredient or a recipe line")
    submit = SubmitField("Add Line")


class ExportToPDFForm(FlaskForm):
    show_checked = BooleanField("Show checked off ingredients: ")
    show_recipes = BooleanField("Show Recipes: ")
    show_lines = BooleanField("Show recipe lines: ")
    submit = SubmitField("Export to PDF")


class ExportToEmailForm(FlaskForm):
    email = StringField("Email to send list to: ")
    submit = SubmitField("Send Email")
