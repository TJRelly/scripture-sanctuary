from api_requests import get_books
BOOKS = get_books()

class SearchService:
    def format_criteria(self, crit):
        formatted = {
            "book": crit[1],
            "chapter": crit[2],
            "translation": crit[0],
            "start": crit[3],
            "end": crit[4],
        }
        return formatted
    
    def format_scripture(self, crit):
        formatted = {
            "book": BOOKS[crit[1] - 1]["name"],
            "chapter": crit[2],
            "trans": crit[0],
            "start": crit[3],
            "end": crit[4],
        }
        return formatted