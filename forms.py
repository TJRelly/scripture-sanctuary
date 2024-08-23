from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    IntegerField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from api_requests import get_books, get_translations

# list of bible translations
TRANSLATIONS = get_translations()
# list of bible books
BOOKS = get_books()

TRANSLATIONS_TUPLES = [
    (
        f"{t['short_name']}",
        (
            f"{t['short_name']} - {t['full_name']}"
            if t["short_name"] != "KJV"
            else f"{t['short_name']} - King James Version, 1769"
        ),
    )
    for t in TRANSLATIONS
]

BOOKS_TUPLES = [(f"{b['bookid']}", f"{b['name']}") for b in BOOKS]


class SearchForm(FlaskForm):
    book = SelectField("Book", choices=BOOKS_TUPLES, validators=[DataRequired()])
    chapter = IntegerField("Chapter", validators=[DataRequired(), NumberRange(min=1)])
    start_verse = IntegerField(
        "From Verse", validators=[Optional(), NumberRange(min=1)]
    )
    end_verse = IntegerField("To Verse", validators=[Optional(), NumberRange(min=1)])
    translation = SelectField(
        "Bible Translation", choices=TRANSLATIONS_TUPLES, validators=[DataRequired()]
    )
    search = SubmitField("Find Verse")


class AddUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=50)])
    first_name = StringField("First Name", validators=[Optional(), Length(max=20)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=20)])
    email = EmailField("Email", validators=[DataRequired(), Length(max=50)])
    profile_img_url = StringField(
        "Profile Image URL",
        validators=[Optional()],
        render_kw={"placeholder": "copy image address"},
    )
    img_url = StringField(
        "Banner Image URL",
        validators=[Optional()],
        render_kw={"placeholder": "copy image address"},
    )


class EditUserForm(FlaskForm):
    username = StringField("Username", validators=[Length(max=20)])
    password = PasswordField("Password", validators=[Length(max=20)])
    first_name = StringField("First Name", validators=[Length(max=20)])
    last_name = StringField("Last Name", validators=[Length(max=20)])
    email = EmailField("Email", validators=[Length(max=50)])
    profile_img_url = StringField(
        "Profile Image", render_kw={"placeholder": "copy image address"}
    )
    img_url = StringField(
        "Banner Image", render_kw={"placeholder": "copy image address"}
    )


class LoginForm(FlaskForm):
    """Form to register users."""

    username = StringField("Username", validators=[DataRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
