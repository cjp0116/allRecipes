import os
from unittest import TestCase
from sqlalchemy import exc
from models import User, db, bcrypt

os.environ['DATABASE_URL'] = 'postgresql:///recipe_test'

from app import app
db.create_all()

class UserModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()
        u1 = User.register("test1", "test1@test.com", "something")
        u2 = User.register("test2", "test2@test.com", "something")

        db.session.commit()
        self.u1 = User.query.get(u1.id)
        self.u2 = User.query.get(u2.id)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        u = User(username="u1", email="u1@u1.com", password="something")
        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.api_posted_likes), 0)

    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)

        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)

        self.assertEqual(self.u1.following[0].id, self.u2.id)
        self.assertEqual(self.u2.followers[0].id, self.u1.id)
    
    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()
        
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(self.u1.following[0].username, self.u2.username)
    
    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(self.u2.followers[0].username, self.u1.username)
    
    def test_registration(self):
        test_user = User.register("test", "test@test.com", "test")
        db.session.commit()

        test_user = User.query.get(test_user.id)
        self.assertEqual(test_user.username, "test")
        self.assertEqual(test_user.email, "test@test.com")
        self.assertTrue(bcrypt.check_password_hash(test_user.password, "test"))
    
    def test_invalid_username_registration(self):
        u = User.register(None, "something@something.com", "something")
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_email_registration(self):
        u = User.register("something", None, "something")
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "something")
        self.assertIsNotNone(u)
        
    
    def test_invalid_authentication(self):
        self.assertFalse(User.authenticate("not the right username", "something"))
        self.assertFalse(User.authenticate(self.u1.username, "not the correct pw"))

    