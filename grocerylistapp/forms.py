from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import URL, DataRequired


class RecipeURLForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    submit = SubmitField("Find Ingredients")


class CustomRecipeForm(FlaskForm):
    name = StringField("Name:")
    recipe_lines = TextAreaField("Ingredients:")
    submit = SubmitField("Find Ingredients")


