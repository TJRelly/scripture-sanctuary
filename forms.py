from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SelectField, StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange
from api_requests import get_books, get_translations

#list of bible translations
TRANSLATIONS = get_translations()
#list of bible books
BOOKS = get_books()

TRANSLATIONS_TUPLES = [(f"{t['short_name']}", f"{t['short_name']} - {t['full_name']}" if t['short_name'] != 'KJV' else f"{t['short_name']} - King James Version, 1769") for t in TRANSLATIONS]

BOOKS_TUPLES = [(f"{b['bookid']}", f"{b['name']}") for b in BOOKS]

class SearchForm(FlaskForm):
    book = SelectField('Book', choices=BOOKS_TUPLES, validators=[DataRequired()])
    chapter = IntegerField('Chapter', validators=[DataRequired(), NumberRange(min=1)])
    start_verse = IntegerField('From Verse', validators=[Optional(), NumberRange(min=1)])
    end_verse = IntegerField('To Verse', validators=[Optional(), NumberRange(min=1)])
    translation = SelectField('Bible Translation', choices=TRANSLATIONS_TUPLES, validators=[DataRequired()])
    search = SubmitField("Find Verse")
    
class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[Optional()])
    email = EmailField('Email', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[Optional()])
    
class EditUserForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    email = EmailField('Email')
    img_url = StringField('Image')