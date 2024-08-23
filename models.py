"""Models for Scripture Sanctuary."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

from sqlalchemy import PrimaryKeyConstraint

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


DEFAULT_IMG = "/static/img/default_img.jpg"

DEFAULT_PROFILE_IMG = "/static/img/default_profile_img.png"

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
    profile_img_url = db.Column(db.String(500), default=DEFAULT_PROFILE_IMG)

    favorites = db.relationship("Favorite", backref="users", cascade="all, delete")
    tags = db.relationship("Tag", backref="users", cascade="all, delete")

    def __repr__(self):
        user = self
        return f"<User id={user.id} username={user.username} password={user.password} first_name={user.first_name} last_name={user.last_name} email={user.email} img_url={user.img_url} profile_img_url={user.profile_img_url}>"
    
    @classmethod
    def register(cls, username, pwd, email, first_name, last_name, img_url, profile_img_url):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name, img_url=img_url, profile_img_url=profile_img_url)
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    name = db.Column(db.Text, unique=True)

    def __repr__(self):
        tag = self
        return f"<Tag id={tag.id} name={tag.name} user_id={tag.user_id}>"


class FavoriteTag(db.Model):
    """Blogly favorite and tag model"""

    __tablename__ = "favorite_tags"

    favorite_id = db.Column(
        db.Integer, db.ForeignKey("favorites.id", ondelete="cascade")
    )
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="cascade"))

    __table_args__ = (PrimaryKeyConstraint("favorite_id", "tag_id"),)

    def __repr__(self):
        favorite_tag = self
        return f"<FavoriteTag favorite_id={favorite_tag.favorite_id} tag_id={favorite_tag.tag_id}>"
