import os
from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, Favorite, User, Tag
from flask import g

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables
db.create_all()
app.config["WTF_CSRF_ENABLED"] = False

class FavoriteViewTestCase(TestCase):
    """Test views for favorites."""
    def setUp(self):
        """Create test client and add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(
            username="testuser",
            pwd="password",
            email="test@test.com",
            first_name="Test",
            last_name="User",
            img_url=None,
            profile_img_url=None,
        )
        self.testuser.id = 1234
        db.session.add(self.testuser)
        db.session.commit()

        self.u1 = User.register(
            username="abc",
            pwd="password",
            email="test1@test.com",
            first_name="First",
            last_name="User",
            img_url=None,
            profile_img_url=None,
        )
        self.u1.id = 111
        db.session.add(self.u1)
        db.session.commit()

        self.test_favorite = Favorite(
            user_id=self.testuser.id,
            book=43,
            chapter=3,
            start=16,
            end=None,
            translation="NIV",
        )
        db.session.add(self.test_favorite)
        db.session.commit()

        self.tag1 = Tag(name="important")
        self.tag2 = Tag(name="inspirational")
        db.session.add_all([self.tag1, self.tag2])
        db.session.commit()
        
    def tearDown(self):
            res = super().tearDown()
            db.session.rollback()
            return res
        
    def test_show_favorite(self):
        """Test if favorite page shows the favorite."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/favorites/{self.test_favorite.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("John 3:16", str(resp.data))

    def test_delete_favorite_logged_out(self):
        """Test that logged-out users cannot delete a favorite."""
        with self.client as c:
            resp = c.post(f"/favorites/{self.test_favorite.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 404)

    def test_edit_favorite(self):
        """Test if user can edit their favorite."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/favorites/{self.test_favorite.id}/edit", data={
                "tags": [self.tag1.name, self.tag2.name]
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            favorite = Favorite.query.get(self.test_favorite.id)
            self.assertIn(self.tag1, favorite.tags)
            self.assertIn(self.tag2, favorite.tags)


