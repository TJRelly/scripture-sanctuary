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
    u1_img = "https://img.freepik.com/free-photo/view-beautiful-rainbow-nature-landscape_23-2151597605.jpg?t=st=1722951178~exp=1722954778~hmac=b24a447f1cf8deb7be5141f28acc3517b5631dfc4f4d74a5874b56c3de3f83f8&w=826"

    user1 = User(
        username="john_doe",
        password=bcrypt.generate_password_hash('password1').decode('utf-8'),
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        img_url=u1_img,
    )
    user2 = User(
        username="jane_smith",
        password=bcrypt.generate_password_hash('password2').decode('utf-8'),
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
    )

    # Create sample tags
    tag1 = Tag(name="Inspiration")
    tag2 = Tag(name="Faith")
    tag3 = Tag(name="Hope")

    # Add users to session
    db.session.add_all([user1, user2])
    db.session.commit()  # Commit to get user IDs

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
