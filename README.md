# Scripture Sanctuary

Scripture Sanctuary is a Flask web application that allows users to search for scriptures, save them as favorites, and organize them by tags/topics. It provides Bible search functionality, user authentication, profile management, and features to help users find and organize their favorite scriptures.

Built using: https://bolls.life/api/ to search bible verses

## Features

- User registration, login, and logout
- Search for Bible scriptures by book, chapter, verse, and translation
- Save favorite scriptures and organize them with custom tags/topics
- View, edit, and delete user profiles
- Manage saved scriptures and tags/topics
- Error handling for duplicate tags/topics, invalid search queries, and user permissions

## Getting Started

Visit the live site: [Scripture Sanctuary](https://scripture-sanctuary.onrender.com/)

### Prerequisites

Before running the application, ensure you have the following installed:

- Python (3.x)
- PostgreSQL
- Pipenv or virtualenv (optional but recommended)
- Node.js (for frontend)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/scripture-sanctuary.git
cd scripture-sanctuary
```

2. **Install dependencies**

Set up your virtual environment:

```bash
pipenv install
```

Activate your virtual environment:

```bash
pipenv shell
```

Install all required Python packages:

```bash
pip install -r requirements.txt
```

3. **Set up the database**

Create your PostgreSQL database:

```bash
createdb scripture-sanctuary
```

Migrate the database:

```bash
flask db upgrade
```

4. **Environment variables**

Create a `.env` file to store environment variables such as your Flask secret key and database URL:

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql:///scripture-sanctuary
```

5. **Run the application**

```bash
flask run
```

Your application should now be running on `http://localhost:5000`.

## Usage

1. **User Authentication**
   - Sign up for a new account or log in using an existing account.
   - You can access your profile page to view your favorite scriptures and manage your tags/topics.

2. **Search Scriptures**
   - Navigate to the search page to search for Bible verses by book, chapter, verse, and translation.
   - Add scriptures to your favorites for easy access later.

3. **Manage Favorites**
   - View your saved scriptures on your profile page.
   - You can edit or delete your saved scriptures and organize them with tags/topics.

4. **Manage tags/topics**
   - Add new tags/topics to organize your saved scriptures.
   - Edit or delete tags/topics as needed from the tags/topics management page.

## Contributing

Feel free to fork the repository and submit pull requests. Contributions are welcome!

### To-Do List

- [ ] Add support for more Bible translations
- [ ] Add password reset functionality
- [ ] Implement social sharing for saved scriptures
- [ ] Add pagination to user and scripture lists

## License

This project is licensed under the MIT License.

