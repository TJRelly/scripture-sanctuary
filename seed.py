from flask_bcrypt import Bcrypt
from app import app
from models import Favorite, Tag, User, db

bcrypt = Bcrypt()

with app.app_context():
    db.drop_all()
    db.create_all()  # This will recreate all tables including favorite_tags
    print("Tables recreated successfully.")


def create_mock_data():
    # Create sample users
    u1_img = "https://cdn.pixabay.com/photo/2016/08/03/09/04/universe-1566161_640.jpg"
    u1_profile_img = "https://images.ctfassets.net/h6goo9gw1hh6/2sNZtFAWOdP1lmQ33VwRN3/24e953b920a9cd0ff2e1d587742a2472/1-intro-photo-final.jpg?w=1200&h=992&fl=progressive&q=70&fm=jpg"
    u2_profile_img = (
        "https://cdn.pixabay.com/photo/2015/03/03/08/55/portrait-657116_640.jpg"
    )
    u3_img = "https://i.pinimg.com/736x/7e/99/fe/7e99fe9f0dc7d4b602577479a1d64f92.jpg"
    u3_profile_img = (
        "https://cdn.inprnt.com/thumbs/b9/9a/b99ae31d32be7d46b45bd659b6fb587b.jpg"
    )

    user1 = User(
        username="john_doe",
        password=bcrypt.generate_password_hash("password1").decode("utf-8"),
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        img_url=u1_img,
        profile_img_url=u1_profile_img,
    )

    user2 = User(
        username="jane_smith",
        password=bcrypt.generate_password_hash("password2").decode("utf-8"),
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        profile_img_url=u2_profile_img,
    )

    user3 = User(
        username="batman",
        password=bcrypt.generate_password_hash("iambatman").decode("utf-8"),
        first_name="Bruce",
        last_name="Wayne",
        email="bruce.wayne@wayneenterpises.com",
        profile_img_url=u3_profile_img,
    )

    # Add users to session
    db.session.add_all([user1, user2, user3])
    db.session.commit()  # Commit to get user IDs

    # Create sample tags
    tag1 = Tag(name="inspiration", user_id=user1.id)
    tag2 = Tag(name="faith", user_id=user1.id)
    tag3 = Tag(name="hope", user_id=user2.id)

    # Create sample favorites and use user_id for association
    favorite1 = Favorite(
        book=1, chapter=1, start=1, end=5, translation="NIV", user_id=user1.id
    )
    favorite2 = Favorite(
        book=2, chapter=3, start=10, end=15, translation="KJV", user_id=user2.id
    )
    favorite3 = Favorite(
        book=3, chapter=4, translation="KJV", user_id=user2.id
    )  # Use user_id instead of user

    # Add tags to favorites
    favorite1.tags.append(tag1)
    favorite1.tags.append(tag2)
    favorite2.tags.append(tag2)
    favorite2.tags.append(tag3)

    # Add tags and favorites to session
    db.session.add_all([tag1, tag2, tag3, favorite1, favorite2, favorite3])

    # Commit the session
    db.session.commit()


create_mock_data()
