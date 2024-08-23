# pip imports
import re
import os

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    flash,
    request,
    session,
)

from flask_debugtoolbar import DebugToolbarExtension
from psycopg2 import IntegrityError
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

load_dotenv()

# created imports
from api_requests import get_books, get_scripture
from forms import AddUserForm, EditUserForm, SearchForm, LoginForm
from models import db, connect_db, User, Favorite, Tag

BOOKS = get_books()

app = Flask(__name__)
app.app_context().push()
# for flask debugtoolbar
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "oh-so-secret")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SUPABASE_URI", "postgresql:///scripture-sanctuary"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

connect_db(app)

CURR_USER_KEY = "curr_user"


@app.errorhandler(404)
def page_not_found(e):
    # You can render a custom 404 page template or return a message
    return render_template("404.html"), 404


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = db.session.get(User, session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = AddUserForm()

    if form.validate_on_submit():
        print(form.errors)
        try:
            user = User.register(
                username=form.username.data,
                pwd=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                img_url=form.img_url.data or None,
                profile_img_url=form.profile_img_url.data or None,
            )

            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("users/signup.html", form=form)

        do_login(user)

        flash("You have registered!", "success")

        return redirect("/")

    else:
        return render_template("users/signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have logged out.", "success")

    return redirect("/")


##############################################################################
# General user routes:


@app.route("/", methods=["GET"])
def home_page():
    """
    Redirects to search page
    """
    return redirect("/search")


@app.route("/users", methods=["GET"])
def show_users():
    """
    Shows all users
    """
    users = db.session.query(User).all()
    return render_template("users/users.html", users=users)


@app.route("/users/<int:user_id>", methods=["GET"])
def user_profile(user_id):
    """
    Gets User by id
    """
    user = User.query.get_or_404((user_id))
    favorites = user.favorites
    scriptures = format_favorite_query(favorites)
    tags = {tag for tag in user.tags} | {
        tag for fav in user.favorites for tag in fav.tags
    }

    return render_template(
        "users/user_profile.html", user=user, scriptures=scriptures, tags=tags
    )


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """Show user details and handle editing"""

    user = User.query.get_or_404(user_id)

    if user.id != g.user.id:
        return redirect("/restricted")

    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user_data = {
            "username": form.username.data,
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "img_url": form.img_url.data
            or user.img_url,  # Use current image URL if none provided
            "profile_img_url": form.profile_img_url.data or user.profile_img_url,
        }

        # password = form.password.data  # Handle password separately if needed

        # Update the user with the new data
        user.username = user_data["username"]
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.email = user_data["email"]
        user.img_url = user_data["img_url"]
        user.profile_img_url = user_data["profile_img_url"]

        # # If password is provided, you might want to hash it before storing
        # if password:
        #     user.password = hash_password(password)  # Replace with your password hashing function

        db.session.commit()

        flash(f"User {user.username}'s details have been updated!", "success")

        return redirect(f"/users/{user_id}")

    return render_template("users/edit_user.html", form=form, user=user)


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """
    deletes a user
    """
    user = User.query.get_or_404(user_id)

    if user.id != g.user.id:
        return redirect("/restricted")

    db.session.delete(user)
    db.session.commit()

    flash(f"{user.username} has been deleted.", "danger")

    return redirect(f"/users")


##############################################################################
# General routes:


@app.route("/restricted")
def restricted():
    """Restricted"""
    flash("You must sign up/log in to perform this action", "danger")
    return redirect("/signup")


##############################################################################
# General favorite routes:


@app.route("/favorites/<int:favorite_id>")
def show_favorite(favorite_id):
    """Shows favorites using id"""

    favorite = Favorite.query.get_or_404(favorite_id)
    time = favorite.created_at.strftime(f"%a %b %d %Y, %-I:%M %p")

    formatted_scripture = format_favorite_query([favorite])[0]

    criteria = get_favorite_criteria(favorite)

    scripture_text = get_scripture(criteria)

    if not scripture_text:
        flash(f"Sorry, scripture not found.", "danger")
        return redirect("/search")

    formatted_verses = []
    for verse in scripture_text:
        formatted_text = remove_strongs_tags(verse["text"])
        formatted_verses.append({"verse": verse["verse"], "text": formatted_text})

    return render_template(
        "favorites/favorite.html",
        favorite=favorite,
        time=time,
        formatted_scripture=formatted_scripture,
        scripture_text=formatted_verses,
    )


@app.route("/favorites/new", methods=["POST"])
def add_favorite():
    """Adds a favorite"""

    criteria = session.get("criteria")

    if not criteria:
        flash("Please enter valid search criteria", "danger")
        return redirect("/")

    # Create a new Favorite object using criteria
    favorite = Favorite(
        user_id=g.user.id,
        book=criteria["book"],
        chapter=criteria["chapter"],
        start=criteria["start"],
        end=criteria["end"],
        translation=criteria["translation"],
    )

    db.session.add(favorite)
    db.session.commit()

    flash("Added successfully, View favorite in your profile", "success")
    return redirect(f"/favorites/{favorite.id}")


@app.route("/favorites/<int:favorite_id>/delete", methods=["POST"])
def delete_favorite(favorite_id):
    """Adds a favorite"""

    favorite = Favorite.query.get(favorite_id)

    db.session.delete(favorite)
    db.session.commit()

    flash("The item has successfully been removed", "success")
    return redirect(f"/users/{g.user.id}")


@app.route("/favorites/<favorite_id>/edit", methods=["GET", "POST"])
def edit_favorite(favorite_id):
    """Shows form to edit favorites"""

    favorite = Favorite.query.get_or_404(favorite_id)

    if favorite.users.id != g.user.id:
        return redirect("/restricted")

    formatted_scripture = format_favorite_query([favorite])[0]["title"]

    tags = Tag.query.all()

    if request.method == "POST":
        favorite.tags = []
        selected_tags = request.form.getlist("tags")

        for tag in selected_tags:
            tag = Tag.query.filter_by(name=tag).first()
            favorite.tags.append(tag)

        db.session.commit()
        return redirect(f"/favorites/{favorite_id}")

    else:
        return render_template(
            "favorites/favorite_edit_form.html",
            favorite=favorite,
            tags=tags,
            formatted_scripture=formatted_scripture,
        )


##############################################################################
# General tag routes:


@app.route("/tags")
def show_tags():
    """show tags page"""

    tags = Tag.query.all()

    return render_template("tags/tags.html", tags=tags)


@app.route("/tags/<int:tag_id>")
def show_tag_details(tag_id):
    """show tag detail page"""

    tag = Tag.query.get_or_404(tag_id)
    scriptures = format_favorite_query(tag.favorites)

    scriptures = []
    for favorite in tag.favorites:
        criteria = get_favorite_criteria(favorite)
        text = get_scripture(criteria)[0]
        scripture_text = remove_strongs_tags(text["text"])
        scripture_title_id = format_favorite_query([favorite])[0]
        more = len(scripture_text) > 1
        scriptures.append(
            {
                "text": scripture_text,
                "title": scripture_title_id["title"],
                "id": scripture_title_id["id"],
                "more": more,
                "verse": text["verse"],
            }
        )

    return render_template("tags/tag_details.html", tag=tag, scriptures=scriptures)


@app.route("/tags/new", methods=["GET", "POST"])
def create_tag():
    """adds tag to database"""

    if request.method == "POST":
        try:
            name = request.form["name"]
            new_tag = Tag(name=name, user_id=g.user.id)

            db.session.add(new_tag)
            db.session.commit()

            flash("You've created a new tag!", "success")
            return redirect("/tags/new")

        except IntegrityError:
            flash("Tag already exists. Please choose a different name.", "danger")

            return redirect("/tags/new")

    else:
        if not g.user:
            return redirect("/restricted")
        return render_template("tags/tag_create_form.html")


@app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
def edit_tag(tag_id):
    """shows edit tag page"""

    if request.method == "POST":
        try:
            new_tag = Tag.query.get_or_404(tag_id)

            new_tag.name = request.form["name"]

            db.session.add(new_tag)
            db.session.commit()

            return redirect("/tags")
        except IntegrityError:
            flash("Tag name already exists.", "danger")
            return redirect(f"/tags/{tag_id}/edit")
    else:
        tag = Tag.query.get_or_404(tag_id)
        if g.user.id != tag.users.id:
            return redirect("/restricted")

    return render_template("tags/tag_edit_form.html", tag=tag)


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """shows edit tag page"""

    tag = Tag.query.get(tag_id)

    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")


##############################################################################
# Search routes:


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

            # Add criteria to session for other routes
            session["criteria"] = {
                "book": book,
                "chapter": chapter,
                "translation": translation,
                "start": start_verse,
                "end": end_verse,
            }

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


def format_favorite_query(query):
    """
    Formats database query into human readable scripture title
    """
    scriptures = []

    for scripture in query:
        id = scripture.id
        scripture = {
            "book": BOOKS[scripture.book - 1]["name"],
            "chapter": scripture.chapter,
            "start": scripture.start,
            "end": scripture.end,
            "trans": scripture.translation,
        }

        formatted_scripture = {"title": format_scripture(scripture), "id": id}
        scriptures.append(formatted_scripture)

    return scriptures


def get_favorite_criteria(favorite):
    """Converts Favorite object into criteria"""
    criteria = [
        favorite.translation,
        favorite.book,
        favorite.chapter,
        favorite.start,
        favorite.end,
    ]
    return criteria
