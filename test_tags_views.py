import os
from unittest import TestCase
from flask import session
from models import db, connect_db, Tag, User, Favorite
from app import app, CURR_USER_KEY
from sqlalchemy.exc import IntegrityError

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Import app
db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class TagViewTestCase(TestCase):
    """Test views for tag-related routes."""

    def setUp(self):
        """Set up test client and sample data."""
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
   
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id

        self.tag1 = Tag(name="TestTag1", user_id=self.testuser.id)
        self.tag2 = Tag(name="TestTag2", user_id=self.testuser.id)

        db.session.add_all([self.testuser, self.tag1, self.tag2])
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_show_tags(self):
        """Test if tags page is displayed correctly."""
        with self.client as c:
            resp = c.get("/tags")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("TestTag1", str(resp.data))
            self.assertIn("TestTag2", str(resp.data))

    def test_show_tag_details(self):
        """Test if tag detail page shows correctly."""
        with self.client as c:
            resp = c.get(f"/tags/{self.tag1.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("TestTag1", str(resp.data))

    def test_create_tag(self):
        """Test tag creation functionality."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/tags/new", data={"name": "NewTag"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            new_tag = Tag.query.filter_by(name="NewTag").first()
            self.assertIsNotNone(new_tag)

    def test_edit_tag(self):
        """Test editing an existing tag."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/tags/{self.tag1.id}/edit", data={"name": "UpdatedTag"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            updated_tag = Tag.query.get(self.tag1.id)
            self.assertEqual(updated_tag.name, "UpdatedTag")

    def test_delete_tag(self):
        """Test if user can delete their own tag."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/tags/{self.tag1.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            

    def test_delete_tag_as_unauthorized_user(self):
        """Test if unauthorized user cannot delete tag."""

        with self.client as c:

            resp = c.post(f"/tags/{self.tag1.id}/delete")
            self.assertEqual(resp.status_code, 302)  # Should redirect due to unauthorized access

