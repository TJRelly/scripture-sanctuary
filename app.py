#pip imports
from flask import Flask, redirect, render_template, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
#created imports
from api_requests import get_books, get_translations
from forms import SearchForm


app = Flask(__name__)
# for flask debugtoolbar
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

#list of bible translations
TRANSLATIONS = get_translations()
#list of bible books
BOOKS = get_books()

@app.route('/', methods=['GET', 'POST'])
def home_page():
    """
    Renders Home Page
    Allows anyone to search a scripture
    Displays an inspiring scripture
    """
    
    form = SearchForm()
    form.translation.choices = [(f"{t['short_name']} - {t['full_name']}") for t in TRANSLATIONS]
    form.book.choices = [(f"{b['name']}") for b in BOOKS]
    
    if form.validate_on_submit():
        book = form.book.data
        chapter = form.chapter.data
        translation = form.translation.data
        start_verse = form.start_verse.data 
        end_verse = form.end_verse.data
        
        scripture = get_scripture()
        
        flash(f"{book} {chapter} : {start_verse} {end_verse} {translation}")
        return render_template("home.html", form=form, scripture=scripture)

    else:
        return render_template("home.html", form=form)
