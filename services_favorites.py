from models import db, Favorite
from api_requests import get_books, get_scripture
import re

BOOKS = get_books()


class FavoriteService:
    def get_fav_by_id(self, favorite_id):
        return Favorite.query.get_or_404(favorite_id)

    def format_scripture(self, scripture):
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

    def format_favorite_query(self, query):
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

            formatted_scripture = {"title": self.format_scripture(scripture), "id": id}
            scriptures.append(formatted_scripture)

        return scriptures

    def get_favorite_criteria(self, favorite):
        """Converts Favorite object into criteria"""
        criteria = [
            favorite.translation,
            favorite.book,
            favorite.chapter,
            favorite.start,
            favorite.end,
        ]
        return criteria

    def remove_strongs_tags(self, text):
        """
        Remove <S> tags and their content from the given text.
        """
        return re.sub(r"<S>\d+</S>", "", text)

    def format_verses(self, text):
        formatted_verses = []
        for verse in text:
            formatted_text = self.remove_strongs_tags(verse["text"])
            formatted_verses.append({"verse": verse["verse"], "text": formatted_text})
        return formatted_verses

    def create_new_fav(self, criteria, user):
        favorite = Favorite(
            user_id=user.id,
            book=criteria["book"],
            chapter=criteria["chapter"],
            start=criteria["start"],
            end=criteria["end"],
            translation=criteria["translation"],
        )

        db.session.add(favorite)
        db.session.commit()
        return favorite

    def delete_fav(self, fav):
        db.session.delete(fav)
        db.session.commit()

    def get_scriptures(self, tag):
        scriptures = []

        for favorite in tag.favorites:
            criteria = self.get_favorite_criteria(favorite)
            text = get_scripture(criteria)[0]
            scripture_text = self.remove_strongs_tags(text["text"])
            scripture_title_id = self.format_favorite_query([favorite])[0]
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
            
        return scriptures
