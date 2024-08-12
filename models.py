"""Models for Scripture Sanctuary."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import PrimaryKeyConstraint

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
DEFAULT_IMG = "https://img.freepik.com/free-photo/river-surrounded-by-forests-cloudy-sky-thuringia-germany_181624-30863.jpg?t=st=1722951363~exp=1722954963~hmac=36e6cce6a32577e34e6c6bb28a6a9537e16265993e05de4266a4409cbf050987&w=996"

class User(db.Model):
    """Scripture Sanctuary user model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(500), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    first_name = db.Column(db.String(500))
    last_name = db.Column(db.String(500))
    email = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), default=DEFAULT_IMG)

    favorites = db.relationship("Favorite", backref="users", cascade="all, delete")

    def __repr__(self):
        user = self
        return f"<User id={user.id} username={user.username} password={user.password} first_name={user.first_name} last_name={user.last_name} email={user.email}>"


class Favorite(db.Model):
    """Scripture Sanctuary favorites model"""

    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book = db.Column(db.Integer, nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    translation = db.Column(db.String(25), nullable=False)

    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))

    tags = db.relationship("Tag", secondary="favorite_tags", backref="favorites")

    def __repr__(self):
        favorite = self
        return f"<Favorite id={favorite.id} book={favorite.book} chapter={favorite.chapter} start={favorite.start} end={favorite.end} translation={favorite.translation} created_at={favorite.created_at} user={favorite.users.username}>"


class Tag(db.Model):
    """Scripture Sanctuary tag model"""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True)

    def __repr__(self):
        tag = self
        return f"<Tag id={tag.id} name={tag.name}>"


class FavoriteTag(db.Model):
    """Blogly favorite and tag model""" 
    
    __tablename__ = "favorite_tags"
    
    favorite_id = db.Column(db.Integer, db.ForeignKey('favorites.id', ondelete="cascade"))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="cascade"))
    
    __table_args__ = (
        PrimaryKeyConstraint('favorite_id', 'tag_id'),
    )
    
    def __repr__(self):
        favorite_tag = self
        return f"<FavoriteTag favorite_id={favorite_tag.favorite_id} tag_id={favorite_tag.tag_id}>"

# Find user favorites
def get_user_favs():
    favorites = db.session.query(User, Favorite).join(Favorite).all()

    for user, favorite in favorites:
        print(user.first_name, user.last_name, favorite)