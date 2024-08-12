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
from forms import AddUserForm, EditUserForm, SearchForm
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
    return render_template("users.html", users=users)


@app.route("/users/new", methods=["GET", "POST"])
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():
        # Add the user to the database
        new_user = User(
            username=form.username.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            img_url=form.img_url.data or None,
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f"You've added {new_user.username}", "success")
            return redirect(url_for('get_users'))  # Redirect to the list of users after successful addition
        
        except Exception as e:  # Catch any exceptions
            db.session.rollback()
            dup = db.session.query(User).filter(User.username == new_user.username).all()
            
            if dup:
                flash("Username/Password already exists.", "danger")
                return redirect(url_for("add_user"))
            else:
                flash(f"An error occurred: {str(e)}", "danger")
                return redirect(url_for("add_user"))
    
    return render_template("add_user.html", form=form)


@app.route("/users/<user_id>", methods=["GET"])
def user_profile(user_id):
    """
    Gets User by id
    """
    user = User.query.get_or_404(user_id)
    favorites = user.favorites
    scriptures = format_favorite_query(favorites)

    return render_template("user_profile.html", user=user, scriptures=scriptures)

@app.route("/users/<user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """Show user details and handle editing"""
    
    user = User.query.get_or_404(user_id)
    
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        user_data = {
            "username": form.username.data,
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "img_url": form.img_url.data or user.img_url,  # Use current image URL if none provided
        }
        
        # password = form.password.data  # Handle password separately if needed

        # Update the user with the new data
        user.username = user_data["username"]
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.email = user_data["email"]
        user.img_url = user_data["img_url"]

        # # If password is provided, you might want to hash it before storing
        # if password:
        #     user.password = hash_password(password)  # Replace with your password hashing function
        
        db.session.commit()
        
        flash(f"User {user.username}'s details have been updated!", "success")
        
        return redirect(f"/users/{user_id}")
    
    return render_template("edit_user.html", form=form, user=user)

@app.route('/users/<user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """
    deletes a user
    only: admin or correct user
    """
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f"{user.username} has been deleted.", "danger")
    
    return redirect(f'/users')

@app.route("/favorites/<favorite_id>")
def show_favorite(favorite_id):
    """Shows posts using id"""

    favorite = Favorite.query.get_or_404(favorite_id)
    time = favorite.created_at.strftime(f"%a %b %d %Y, %-I:%M %p")

    return render_template("favorite.html", favorite=favorite, time=time)


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


def format_favorite_query(query):
    """
    Formats database query into human readable scripture
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
