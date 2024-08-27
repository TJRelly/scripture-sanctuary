# pip imports
import os

from flask import Flask, g, redirect, render_template, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension
from psycopg2 import IntegrityError
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

load_dotenv()

# created imports
from api_requests import get_scripture
from forms import AddUserForm, EditUserForm, SearchForm, LoginForm
from models import db, connect_db, User, Favorite, Tag

from services_users import UserService
from services_favorites import FavoriteService
from services_tags import TagService
from services_search import SearchService

# Instantiate the service classes
user_service = UserService()
favorite_service = FavoriteService()
tag_service = TagService()
search_service = SearchService()

app = Flask(__name__)
app.app_context().push()
# for flask debugtoolbar
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "oh-so-secret")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SUPABASE_DB_URI", "postgresql:///scripture-sanctuary"
)

# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///scripture-sanctuary-test"

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
    user = user_service.get_user_by_id(user_id)
    scriptures = favorite_service.format_favorite_query(user.favorites)
    tags = user_service.get_user_tags(user_id)

    return render_template(
        "users/user_profile.html", user=user, scriptures=scriptures, tags=tags
    )


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """Show user details and handle editing"""

    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = EditUserForm(obj=g.user)

    if form.validate_on_submit():
        user_data = {
            "username": form.username.data,
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "img_url": form.img_url.data or User.__table__.columns.img_url.default.arg,
            "profile_img_url": form.profile_img_url.data
            or User.__table__.columns.profile_img_url.default.arg,
            "password": form.password.data,
        }

        # Update the user with the new data
        user_service.update_user(g.user, user_data)

        flash(f"User {g.user.username}'s details have been updated!", "success")

        return redirect(f"/users/{user_id}")

    return render_template("users/edit_user.html", form=form, user=g.user)


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """
    deletes a user
    """

    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_service.delete_user(g.user)

    flash(f"{g.user.username} has been deleted.", "danger")

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
    formatted_scripture = favorite_service.format_favorite_query([favorite])[0]
    criteria = favorite_service.get_favorite_criteria(favorite)
    scripture_text = get_scripture(criteria)

    if not scripture_text:
        flash(f"Sorry, scripture not found.", "danger")
        return redirect("/search")

    formatted_verses = favorite_service.format_verses(scripture_text)

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
    if g.user:
        # Create a new Favorite object using criteria
        favorite = favorite_service.create_new_fav(criteria, g.user)

        flash("Added successfully, View favorite in your profile", "success")
        return redirect(f"/favorites/{favorite.id}")

    flash("Unauthorized", "danger")
    return redirect("/")


@app.route("/favorites/<int:favorite_id>/delete", methods=["POST"])
def delete_favorite(favorite_id):
    """Adds a favorite"""

    favorite = favorite_service.get_fav_by_id(favorite_id)

    if not g.user or g.user.id != favorite.users.id:
        flash("Unauthorized", "danger")
        return redirect("/")

    favorite_service.delete_fav(favorite)

    flash("The item has successfully been removed", "success")
    return redirect(f"/users/{g.user.id}")


@app.route("/favorites/<favorite_id>/edit", methods=["GET", "POST"])
def edit_favorite(favorite_id):
    """Shows form to edit favorites"""

    favorite = favorite_service.get_fav_by_id(favorite_id)

    if not g.user.id or g.user.id != favorite.users.id:
        flash("Unauthorized", "danger")
        return redirect("/")

    formatted_scripture = favorite_service.format_favorite_query([favorite])[0]["title"]

    tags = tag_service.get_all_tags()

    if request.method == "POST":
        selected_tags = request.form.getlist("tags")

        tag_service.save_favorite_tags(favorite, selected_tags)

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

    tags = tag_service.get_all_tags()

    return render_template("tags/tags.html", tags=tags)


@app.route("/tags/<int:tag_id>")
def show_tag_details(tag_id):
    """show tag detail page"""

    tag = Tag.query.get_or_404(tag_id)

    scriptures = favorite_service.get_scriptures(tag)

    return render_template("tags/tag_details.html", tag=tag, scriptures=scriptures)


@app.route("/tags/new", methods=["GET", "POST"])
def create_tag():
    """adds tag to database"""

    if request.method == "POST":
        try:
            name = request.form["name"]
            tag_service.save_new_tag(g.user, name)

            flash("You've created a new tag!", "success")
            return redirect("/tags/new")

        except IntegrityError:
            flash("Tag already exists. Please choose a different name.", "danger")
            return redirect("/tags/new")

    else:
        if not g.user:
            flash("Unauthorized", "danger")
            return redirect("/")
        return render_template("tags/tag_create_form.html")


@app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
def edit_tag(tag_id):
    """shows edit tag page"""

    if request.method == "POST":
        try:
            new_tag = tag_service.get_tag_by_id(tag_id)
            name = request.form["name"]
            tag_service.edit_tag(new_tag, name)

            return redirect("/tags")
        except IntegrityError:
            flash("Tag name already exists.", "danger")
            return redirect(f"/tags/{tag_id}/edit")
    else:
        tag = tag_service.get_tag_by_id(tag_id)
        if not g.user or g.user.id != tag.users.id:
            flash("Unauthorized", "danger")
            return redirect("/")

    return render_template("tags/tag_edit_form.html", tag=tag)


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """shows edit tag page"""
    tag = tag_service.get_tag_by_id(tag_id)

    if not g.user or g.user.id != tag.user_id:
        flash("Unauthorized", "danger")
        return redirect("/")

    tag_service.delete_tag(tag)

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
            session["criteria"] = search_service.format_criteria(criteria)

            # uses form data to make api request
            scripture_text = get_scripture(criteria)

            if not scripture_text:
                flash(f"Sorry, scripture not found.", "danger")
                return redirect("/search")

            verses = favorite_service.format_verses(scripture_text)
            scripture = search_service.format_scripture(criteria)
            formatted_scripture = favorite_service.format_scripture(scripture)

            return render_template(
                "search.html",
                form=form,
                scripture_text=verses,
                formatted_scripture=formatted_scripture,
            )
        else:
            # Form is not valid
            print(f"Form errors: {form.errors}")
            flash("Internal Server Error", "danger")
            return redirect("/search")

    else:
        return render_template("search.html", form=form)
