import requests

MOST_READ = ["NIV", "KJV", "NKJV", "ESV", "NLT", "NASB", "MSG"]

def get_translations():
    """
    Returns a list of popular bible translations: 
    ["abbrevation - full name"]
    """
    english_translations = requests.get("https://bolls.life/static/bolls/app/views/languages.json").json()[4]
    
    popular_translations = [{'short_name' : t['short_name'], 'full_name':t['full_name']} for t in english_translations['translations'] if t['short_name'] in MOST_READ]
    
    return popular_translations

def get_books():
    """
    Return a list of 66 bible books: 
    {"bookid", "name", "chronorder", "chapters"}
    """
    books = requests.get("https://bolls.life/static/bolls/app/views/translations_books.json").json()['YLT']
    
    return books

# def get_scripture(criteria):
#     """Returns scripture w/verse or verses from form data"""
#     try:
#         translation, book, chapter, start_verse, end_verse = criteria
        
#         request_data = [
#             {
#                 "translation": translation,
#                 "book": book,
#                 "chapter": chapter,
#                 "verses": list(range(int(start_verse), int(end_verse) + 1))
#             }
#         ]
        
#         # Send the POST request to the '/get-verses/' endpoint
#         response = requests.post('https://bolls.life/get-verses/', headers={'Content-Type': 'application/json'}, json=request_data)

#         if response.status_code == 200:
#             print(response.json())
#             return response.json()
#         else:
#             # Handle non-200 status code cases
#             print(f"Error fetching scripture: {response.status_code} - {response.text}")
#             return None
    
#     except Exception as e:
#         # Handle any exceptions raised during the process
#         print(f"An error occurred: {e}")
#         return None

# get chapter

def get_scripture(criteria):
    """
    Returns scripture(s) based on chapter and selected verse or verses
    
    """
    try:
        translation, book, chapter, start_verse, end_verse = criteria
        
        # Send the Get requests to'/get-text/' depending on input
        request_chapter = f'https://bolls.life/get-chapter/{translation}/{book}/{chapter}'
        
        # Get the whole chapter
        
        
        response = requests.get(request_chapter)
        chapter = response.json()
        
        if response.status_code == 200:
            if start_verse and end_verse:
                verses = [chapter[verse] for verse in range(start_verse-1, end_verse)]    
                return verses
            elif start_verse:
                print(chapter[start_verse-1])
                return [chapter[start_verse-1]]
            elif end_verse:
                verses = [chapter[verse] for verse in range(0, end_verse)]    
                return verses
            else:
                return chapter
        else:
            # Handle non-200 status code cases
            print(f"Error fetching scripture: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        # Handle any exceptions raised during the process
        print(f"An error occurred: {e}")
        return None