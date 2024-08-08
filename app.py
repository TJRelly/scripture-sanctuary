# pip imports
import re
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    flash,
    url_for,
    request,
    session,
)
from flask_debugtoolbar import DebugToolbarExtension

# created imports
from api_requests import get_books, get_translations, get_scripture
from forms import SearchForm
from models import db, connect_db, User, Favorite, Tag, FavoriteTag

BOOKS = get_books()

app = Flask(__name__)
app.app_context().push()
# for flask debugtoolbar
app.config["SECRET_KEY"] = "oh-so-secret"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///scripture-sanctuary"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

connect_db(app)


@app.route("/", methods=["GET"])
def home_page():
    """
    Redirects to search page
    """
    return redirect("/search")


@app.route("/users", methods=["GET"])
def get_users():
    """
    Gets Users
    """
    users = db.session.query(User).all()
    return render_template("get_users.html", users=users)


@app.route("/users/<user_id>", methods=["GET"])
def user_profile(user_id):
    """
    Gets User by id
    """
    user = User.query.get_or_404(user_id)
    favorites = user.favorites
    scriptures = []

    for scripture in favorites:
        id = scripture.id
        scripture = {
            "book": BOOKS[scripture.book - 1]["name"],
            "chapter": scripture.chapter,
            "start": scripture.start,
            "end": scripture.end,
            "trans": scripture.translation,
        }

        print(scripture)
        formatted_scripture = {"title": format_scripture(scripture), "id": id}
        scriptures.append(formatted_scripture)

    return render_template("user_profile.html", user=user, scriptures=scriptures)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    Allows anyone to search a scripture
    Displays Scripture
    Displays an inspiring scripture
    """

    form = SearchForm()

    if request.method == "POST":

        if form.validate_on_submit():
            book = int(form.book.data)
            chapter = form.chapter.data
            translation = form.translation.data
            start_verse = form.start_verse.data
            end_verse = form.end_verse.data

            criteria = [translation, book, chapter, start_verse, end_verse]

            # uses form data to make api request
            scripture_text = get_scripture(criteria)

            if not scripture_text:
                flash(f"Sorry, scripture not found.", "danger")
                return redirect("/search")

            formatted_verses = []
            for verse in scripture_text:
                formatted_text = remove_strongs_tags(verse["text"])
                formatted_verses.append(
                    {"verse": verse["verse"], "text": formatted_text}
                )

            scripture = {
                "book": BOOKS[book - 1]["name"],
                "chapter": chapter,
                "start": start_verse,
                "end": end_verse,
                "trans": translation,
            }

            formatted_scripture = format_scripture(scripture)

            return render_template(
                "search.html",
                form=form,
                scripture_text=formatted_verses,
                formatted_scripture=formatted_scripture,
            )
        else:
            # Form is not valid
            print(f"Form errors: {form.errors}")
            flash("Error on form")
            return redirect("/search")

    else:
        return render_template("search.html", form=form)


# helper functions
def format_scripture(scripture):
    """
    input: scripture obj
    output: formatted string
    """
    start_verse = scripture["start"]
    end_verse = scripture["end"]

    formatted_scripture = f"{scripture['book']} {scripture['chapter']}"

    if start_verse and end_verse:
        formatted_scripture += (
            f":{scripture['start']}-{scripture['end']} ({scripture['trans']})"
        )
    elif start_verse:
        formatted_scripture += f":{scripture['start']} ({scripture['trans']})"
    elif end_verse:
        formatted_scripture += f":1-{scripture['end']} ({scripture['trans']})"
    else:
        formatted_scripture += f" ({scripture['trans']})"

    return formatted_scripture


def remove_strongs_tags(text):
    """
    Remove <S> tags and their content from the given text.
    """
    return re.sub(r"<S>\d+</S>", "", text)
