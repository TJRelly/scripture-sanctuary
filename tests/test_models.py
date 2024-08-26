"""Models tests for Scripture Sanctuary."""

from unittest import TestCase
from app import app

from models import (
    db,
    User,
    Favorite,
    Tag,
    FavoriteTag,
    DEFAULT_IMG,
    DEFAULT_PROFILE_IMG,
)

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

from app import app

# Create a test database
db.create_all()


class UserModelTestCase(TestCase):
    """Test models for User."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u = User.register(
            username="testuser",
            pwd="password",
            email="test@test.com",
            first_name="Test",
            last_name="User",
            img_url=None,
            profile_img_url=None,
        )
        u.id = 1234
        db.session.add(u)
        db.session.commit()

        self.uid = u.id
        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_repr(self):
        """Does the repr method work?"""
        self.assertEqual(
            repr(self.u),
            f"<User id={self.uid} username=testuser password={self.u.password} first_name=Test last_name=User email=test@test.com img_url={DEFAULT_IMG} profile_img_url={DEFAULT_PROFILE_IMG}>",
        )

    def test_user_authentication(self):
        """Can a user be authenticated?"""
        self.assertTrue(User.authenticate("testuser", "password"))
        self.assertFalse(User.authenticate("testuser", "wrongpassword"))


class FavoriteModelTestCase(TestCase):
    """Test models for Favorite."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u = User.register(
            username="testuser",
            pwd="password",
            email="test@test.com",
            first_name="Test",
            last_name="User",
            img_url=None,
            profile_img_url=None,
        )
        u.id = 1234
        db.session.add(u)
        db.session.commit()

        self.uid = u.id
        self.u = User.query.get(self.uid)

        f = Favorite(
            book=1, chapter=1, start=1, end=10, translation="NIV", user_id=self.uid
        )
        db.session.add(f)
        db.session.commit()

        self.fid = f.id
        self.f = Favorite.query.get(self.fid)

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_favorite_repr(self):
        """Does the repr method work?"""
        self.assertEqual(
            repr(self.f),
            f"<Favorite id={self.fid} book=1 chapter=1 start=1 end=10 translation=NIV created_at={self.f.created_at} user={self.u.username}>",
        )


class TagModelTestCase(TestCase):
    """Test models for Tag."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u = User.register(
            username="testuser",
            pwd="password",
            email="test@test.com",
            first_name="Test",
            last_name="User",
            img_url=None,
            profile_img_url=None,
        )
        u.id = 1234
        db.session.add(u)
        db.session.commit()

        self.uid = u.id
        self.u = User.query.get(self.uid)

        t = Tag(name="Favorite Tag", user_id=self.uid)
        db.session.add(t)
        db.session.commit()

        self.tid = t.id
        self.t = Tag.query.get(self.tid)

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_tag_repr(self):
        """Does the repr method work?"""
        self.assertEqual(
            repr(self.t), f"<Tag id={self.tid} name=Favorite Tag user_id={self.uid}>"
        )


class FavoriteTagModelTestCase(TestCase):
    """Test models for FavoriteTag."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u = User.register(
            username="testuser",
            pwd="password",
            email="test@test.com",
            first_name="Test",
            last_name="User",
            img_url=None,
            profile_img_url=None,
        )
        u.id = 1234
        db.session.add(u)
        db.session.commit()

        self.uid = u.id
        self.u = User.query.get(self.uid)

        f = Favorite(
            book=1, chapter=1, start=1, end=10, translation="NIV", user_id=self.uid
        )
        db.session.add(f)
        db.session.commit()

        t = Tag(name="Favorite Tag", user_id=self.uid)
        db.session.add(t)
        db.session.commit()

        self.fid = f.id
        self.tid = t.id

        ft = FavoriteTag(favorite_id=self.fid, tag_id=self.tid)
        db.session.add(ft)
        db.session.commit()

        self.ftid = ft.favorite_id
        self.fttagid = ft.tag_id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_favorite_tag_repr(self):
        """Does the repr method work?"""
        self.assertEqual(
            repr(
                FavoriteTag.query.filter_by(
                    favorite_id=self.ftid, tag_id=self.fttagid
                ).first()
            ),
            f"<FavoriteTag favorite_id={self.ftid} tag_id={self.fttagid}>",
        )
