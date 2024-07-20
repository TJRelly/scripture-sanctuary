from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    book = SelectField('Book', choices=[], validators=[DataRequired()])
    chapter = IntegerField('Chapter', validators=[DataRequired()])
    translation = SelectField('Bible Translation', choices=[], validators=[DataRequired()])
    start_verse = SelectField('Start Verse', choices=[])
    end_verse = SelectField('End Verse', choices=[])
    submit = SubmitField('Search')