from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Follows(db.Model):
    __tablename__ = 'follows'

    user_being_followed_id = db.Column(db.Integer,
                                       db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    user_following_id = db.Column(db.Integer,
                                  db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png")
    api_posted_likes = db.Column(db.Integer)
    bio = db.Column(db.Text)
    location = db.Column(db.Text)

    followers = db.relationship(
        "User",
        secondary='follows',
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )
    following = db.relationship(
        'User',
        secondary='follows',
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )
    posts = db.relationship("User_Recipe_Post")
    likes = db.relationship("Like")
    comments = db.relationship("Comment")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} username={self.username}>"

    @classmethod
    def register(cls, username, email, password):
        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(
            username=username,
            email=email,
            password=hashed_pw
        )
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, pw):
        user = cls.query.filter_by(username=username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, pw)
            if is_auth:
                return user
        return False

class User_Recipe_Post(db.Model):
    __tablename__ = 'user_recipe_posts'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete="cascade"),
        nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    recipe_title = db.Column(db.Text, nullable=False)
    recipe_ingredients = db.Column(db.Text, nullable=False)
    recipe_instructions = db.Column(db.Text, nullable=False)

    external_id = db.Column(db.Integer)
    recipe_image = db.Column(db.Text)
    comments = db.relationship("Comment")
    likes = db.relationship("Like")
    def __repr__(self):
        return f"<User_Recipe_Post id={self.id} recipe_title={self.recipe_title} >"

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    created_by = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete="cascade"))
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    recipe_post_id = db.Column(
        db.Integer,
        db.ForeignKey('user_recipe_posts.id', ondelete="cascade"))
    posted_by = db.relationship("User")


class Like(db.Model):
    """ Mapping of user likes to recipe posts """

    def __repr__(self):
        return f"< Likes this userid {self.user_id} likes user_posted_recipe_post_id {self.user_posted_recipe_post_id}>"
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"))

    user_posted_recipe_post_id = db.Column(
        db.Integer,
        db.ForeignKey('user_recipe_posts.id', ondelete="cascade"))



def connect_db(app):
    db.app = app
    db.init_app(app)
