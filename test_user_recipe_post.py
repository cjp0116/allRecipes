import os
from unittest import TestCase
from sqlalchemy import exc
from models import User, db, User_Recipe_Post, Comment, Like

os.environ['DATABASE_URL'] = 'postgresql:///recipe_test'

from app import app
db.create_all()

class UserRecipePostTest(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()
        u1 = User.register("test1", "test@test.com", "something")
        u2 = User.register("test2", "test2@test.com", "something")
        db.session.commit()
        self.u1 = User.query.get(u1.id)
        self.u2 = User.query.get(u2.id)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_recipe_post(self):
        p1 = User_Recipe_Post(
            created_by = self.u1.username,
            recipe_title = "testrecipe",
            recipe_ingredients = "1something, 3 something, 6 something",
            recipe_instructions = "idk make it work"
        )
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(len(self.u1.posts), 1)
        self.assertEqual(self.u1.posts[0].recipe_title, "testrecipe")
        self.assertEqual(self.u1.posts[0].recipe_ingredients, "1something, 3 something, 6 something")
        self.assertEqual(self.u1.posts[0].recipe_instructions, "idk make it work")
        self.assertEqual(len(p1.comments), 0)
    
    def test_recipe_post_comments(self):
        p1 = User_Recipe_Post(
            created_by = self.u1.username,
            recipe_title = "testrecipe",
            recipe_ingredients = "1something, 3 something, 6 something",
            recipe_instructions = "idk make it work"
        )
        db.session.add(p1)
        db.session.commit()
        c1 = Comment(
            comment="some comment",
            created_by=self.u1.username,
            recipe_post_id=p1.id
        )

        db.session.add(c1)
        db.session.commit()
        self.assertEqual(len(p1.comments), 1)
        self.assertEqual(p1.comments[0].comment, "some comment")
        self.assertEqual(p1.comments[0].created_by, "test1")
        self.assertEqual(p1.comments[0].recipe_post_id, p1.id)


        c2 = Comment(
            comment="second comment",
            created_by= self.u2.username,
            recipe_post_id= p1.id
        )
        db.session.add(c2)
        db.session.commit()
        self.assertEqual(len(p1.comments), 2)
        self.assertEqual(p1.comments[1].comment, "second comment")
        self.assertEqual(p1.comments[1].created_by, "test2")
        self.assertEqual(p1.comments[1].recipe_post_id, p1.id)
    
    def test_recipe_post_likes(self):
        p1 = User_Recipe_Post(
            created_by = self.u1.username,
            recipe_title = "testrecipe",
            recipe_ingredients = "1something, 3 something, 6 something",
            recipe_instructions = "idk make it work"
        )
        db.session.add(p1)
        db.session.commit()
        like1 = Like(user_id=self.u1.id, user_posted_recipe_post_id=p1.id)
        
        db.session.add(like1)
        db.session.commit()
        self.assertEqual(len(p1.likes), 1)
        self.assertEqual(p1.likes[0].user_id, self.u1.id)

        like2 = Like(user_id=self.u2.id, user_posted_recipe_post_id=p1.id)
        db.session.add(like2)
        db.session.commit()
        self.assertEqual(len(p1.likes), 2)
        self.assertEqual(p1.likes[1].user_id, self.u2.id)
        