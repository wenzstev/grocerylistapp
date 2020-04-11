import secrets

from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from itsdangerous import JSONWebSignatureSerializer as Serializer

from flask import current_app
from flask_login import UserMixin

from grocerylistapp import db, login_manager


def get_hex_id():   # helper function for generating hex identifiers
    return secrets.token_urlsafe(8)


class RecipeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # the primary key
    name = db.Column(db.String, nullable=False)  # name for recipe (from url)
    hex_name = db.Column(db.String(20), unique=True, nullable=False)  # name for database #TODO use hex_id() function
    hex_color = db.Column(db.String(6), nullable=False)  # randomly generated color for use in lists
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # image for list
    recipe_url = db.Column(db.String(200))
    compiled_list = db.Column(db.ForeignKey('compiled_list.id'))    # the id of the compiled list
    lines = db.relationship('RawLine', backref='rlist', lazy=True)  # the lines of the list

    def __repr__(self):
        return f"{self.hex_name} -- {self.recipe_url}"


class CompiledList(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # the primary key
    name = db.Column(db.String(20), nullable=False, default="Unnamed List")  # user created name, optional
    hex_name = db.Column(db.String(20), unique=True, nullable=False)  # name for database #TODO use hex_id() function
    lines = db.relationship('CleanedLine', backref='list', lazy=True)  # cleaned lines for the list
    recipes = db.relationship('RecipeList', backref='complist', lazy=True)  # all recipes that are in the compiled list
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)  # the id of the user who made the list

    def __repr__(self):
        return f"{self.name}"


line_assocs = db.Table('line_assocs',
                       db.Column('rawline_id', db.Integer, db.ForeignKey('raw_line.id')),
                       db.Column('cleanedline_id', db.Integer, db.ForeignKey('cleaned_line.id'))
                       )


class RawLine(db.Model):
    # TODO: refactor so there are less 'id' labels
    id = db.Column(db.Integer, primary_key=True)  # the primary key
    hex_id = db.Column(db.String(8), default=get_hex_id, nullable=False, unique=True) # hex identifier for requests
    full_text = db.Column(db.String(100), nullable=False)  # the text of the line
    list_id = db.Column(db.Integer, db.ForeignKey('recipe_list.id'))  # the id of the list for the line
    text_to_colors = db.Column(db.String)
    cleaned_lines = db.relationship('CleanedLine', secondary=line_assocs, backref=db.backref('raw_lines', lazy='dynamic'))

    def __repr__(self):
        return f"{self.full_text}"


class CleanedLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)   # the primary key
    index_in_list = db.Column(db.Integer)  # index in the grocery list (for requests) TODO: create this automatically
    hex_id = db.Column(db.String(8), default=get_hex_id, nullable=False, unique=True) # hex identifier for requests
    amount = db.Column(db.Float)    # the amount of ingredient (optional)
    measurement = db.Column(db.String(20))  # the measurement of the amount (optional)
    ingredient = db.Column(db.String(100), nullable=False)  # the ingredient (required)
    checked = db.Column(db.Boolean, default=False)  # whether or not the item is checked off the list
    comp_list = db.Column(db.Integer, db.ForeignKey('compiled_list.id'))

    def __repr__(self):
        return f"{self.ingredient} in list {self.comp_list}"





@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    email_validated = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(60), nullable=False)
    temporary = db.Column(db.Boolean, default=False)  # determines if user account is temporary (for guest users)
    checklists = db.relationship('CompiledList', backref='user', lazy=True)  # the user's grocery lists

    def __repr__(self):
        return f"(User('{self.username}', '{self.email}'"

    def get_reset_token(self, expires_sec=1800):
        s = TimedSerializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    # TODO: combine this with get_reset_token
    def get_validate_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = TimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    # TODO: combine this with verify_reset_token
    @staticmethod
    def verify_email_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)