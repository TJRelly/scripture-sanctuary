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

def get_scripture():
    """Returns scripture from form data"""
    
    scriptu