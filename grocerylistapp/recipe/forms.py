from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField


class RecipeCleanForm(FlaskForm):
    name = StringField('Name:')
    submit = SubmitField("Submit")
