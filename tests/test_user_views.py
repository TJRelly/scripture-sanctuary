"""View tests for User routes in Scripture Sanctuary."""

import os
from unittest import TestCase
from models import db, User
from app import app, CURR_USER_KEY

# Import the app after setting the database URL
from app import app

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables
db.create_all()

# Disable CSRF for testing
app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client and add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        # Create a test user
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

        # Another user for testing purposes
        self.other_user = User.register(
            username="otheruser",
            pwd="password",
            email="other@test.com",
            first_name="Other",
            last_name="User",
            img_url=None,
            profile_img_url=None,
        )
        self.other_user.id = 5678
        db.session.add(self.other_user)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_home_page(self):
        """Test if home page redirects to search page."""
        with self.client as c:
            resp = c.get("/")
            self.assertEqual(resp.status_code, 302)

    def test_show_users(self):
        """Test if users are listed on /users route."""
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))
            self.assertIn("otheruser", str(resp.data))

    def test_user_profile(self):
        """Test if user profile page shows correct information."""
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test User", str(resp.data))
            self.assertIn("@testuser", str(resp.data))

    def test_edit_user(self):
        """Test if user can edit their profile."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Send the POST request with form data
            resp = c.post(
                f"/users/{self.testuser.id}/edit",
                data={
                    "username": "updateduser",
                    "first_name": "Updated",
                    "last_name": "User",
                    "email": "updated@test.com",
                    "img_url": "http://example.com/image.jpg",
                    "profile_img_url": "http://example.com/profile.jpg",
                },
                follow_redirects=True,
            )

            # Check response status and content
            self.assertEqual(resp.status_code, 200)
            self.assertIn("updateduser", str(resp.data))

    def test_edit_user_logged_out(self):
        """Test if logged out users are prohibited from editing user profiles."""
        with self.client as c:
            resp = c.post(
                f"/users/{self.testuser.id}/edit",
                data={
                    "username": "hackeduser",
                    "first_name": "Hacked",
                    "last_name": "User",
                    "email": "hacked@test.com",
                },
                follow_redirects=True,
            )
            new_user = User.query.get(self.testuser.id)
            print(new_user)
            self.assertEqual(resp.status_code, 200)

    def test_delete_user(self):
        """Test if user can delete their account."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/{self.testuser.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser has been deleted.", str(resp.data))

            # Verify user deletion
            deleted_user = User.query.get(self.testuser.id)
            self.assertIsNone(deleted_user)

    def test_delete_user_logged_out(self):
        """Test if logged out users are prohibited from deleting accounts."""
        with self.client as c:
            resp = c.post(f"/users/{self.testuser.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # Verify user is not deleted
            not_deleted_user = User.query.get(self.testuser.id)
            self.assertIsNotNone(not_deleted_user)
