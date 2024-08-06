"""Models for Scripture Sanctuary."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import PrimaryKeyConstraint

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    """Scripture Sanctuary user model"""
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    favorites = db.relationship('Favorite', backref='users', cascade="all, delete")
    
    def __repr__(self):
        user = self
        return f"<User id={user.id} first_name= {user.first_name} last_name= {user.last_name} img_url={user.image_url}>"
 
class Favorite(db.Model):
    """Scripture Sanctuary favorites model""" 
    
    __tablename__ = "favorites"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    translation = db.Column(db.String(25), nullable=False)
    book = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))
    
    tags = db.relationship('Tag', secondary='favorite_tags', backref='favorites')
    
    def __repr__(self):
        favorite = self
        return f"<Favorite id={favorite.id} title= {favorite.title} content= {favorite.content} created_at={favorite.created_at} user= {favorite.users.first_name} {favorite.users.last_name}>"
    
class Tag(db.Model):
    """Scripture Sanctuary tag model""" 
    
    __tablename__ = "tags"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True)
    
    def __repr__(self):
        tag = self
        return f"<Tag id={tag.id} name={tag.name}>"
    
class FavoriteTag(db.Model):
    """Scripture Sanctuary favorite and tag model""" 
    
    __tablename__ = "favorite_tags"
    
    favorite_id = db.Column(db.Integer, db.ForeignKey('favorites.id', ondelete="cascade"))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="cascade"))
    
    __table_args__ = (
        PrimaryKeyConstraint('favorite_id', 'tag_id'),
    )
    
    def __repr__(self):
        favorite_tag = self
        return f"<FavoriteTag favorite_id={favorite_tag.favorite_id} tag_id={favorite_tag.tag_id}>"
    
# last name, first name, title of favorite
def get_name_title():
    favorites = db.session.query(User, Favorite).join(Favorite).all()
    
    for user, favorite in favorites:
        print(user.first_name, user.last_name, favorite)