import requests

MOST_READ = ["NIV", "KJV", "NKJV", "ESV", "NLT", "NASB", "MSG"]
BASE_URL = "https://bolls.life"


def get_translations():
    """
    Returns a list of popular bible translations:
    ["abbrevation - full name"]
    """
    try:
        response = requests.get(f"{BASE_URL}/static/bolls/app/views/languages.json")
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        english_translations = [
            entry for entry in response.json() if entry["language"] == "English"
        ][0]

        print(english_translations)  # Ensure MOST_READ is printed

        popular_translations = [
            {"short_name": t["short_name"], "full_name": t["full_name"]}
            for t in english_translations["translations"]
            if t["short_name"] in MOST_READ
        ]

        return popular_translations

    except requests.exceptions.RequestException as e:
        print(f"Error fetching translations: {e}")
        return []


def get_books():
    """
    Return a list of 66 bible books:
    {"bookid", "name", "chronorder", "chapters"}
    """
    books = requests.get(
        f"{BASE_URL}/static/bolls/app/views/translations_books.json"
    ).json()["YLT"]

    return books


def get_scripture(criteria):
    """
    Returns scripture(s) based on chapter and selected verse or verses

    """
    try:
        translation, book, chapter, start_verse, end_verse = criteria

        # Send the Get requests to'/get-text/' depending on input
        request_chapter = f"{BASE_URL}/get-chapter/{translation}/{book}/{chapter}"

        # Get the whole chapter

        response = requests.get(request_chapter)
        chapter = response.json()

        if response.status_code == 200:
            if start_verse and end_verse:
                verses = [chapter[verse] for verse in range(start_verse - 1, end_verse)]
                return verses
            elif start_verse:
                return [chapter[start_verse - 1]]
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
