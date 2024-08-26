from models import db, Tag
from api_requests import get_books


BOOKS = get_books()


class TagService:
    def get_tag_by_id(self, id):
        tag = Tag.query.get_or_404(id)
        return tag
        
    def get_all_tags(self):
        tags = Tag.query.all()
        return tags

    def save_favorite_tags(self, fav, selected):
        fav.tags = []
        for tag in selected:
            tag = Tag.query.filter_by(name=tag).first()
            fav.tags.append(tag)
        print(fav.tags)
        db.session.commit()

    def save_new_tag(self, user, title):
        new_tag = Tag(name=title, user_id=user.id)

        db.session.add(new_tag)
        db.session.commit() 

    def edit_tag(self, tag, name):
        tag.name = name
        db.session.add(tag)
        db.session.commit() 
    
    def delete_tag(self, tag):
        db.session.delete(tag)
        db.session.commit()