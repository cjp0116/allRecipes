import os
import json

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, User_Recipe_Post, Comment, Like, Follows
from API import SpoonacularAPI


CURR_USER_KEY = 'curr_user'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABSE_URL', 'postgres:///recipes'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "seomthing")
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
toolbar = DebugToolbarExtension(app)


connect_db(app)


def setUp():
    db.drop_all()
    db.create_all()
    User.register("api", "api@api.com", "api")
    db.session.commit()


def do_login(user):
    session[CURR_USER_KEY] = user.id


def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.before_request
def add_user_to_g():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


@app.route("/register", methods=['GET', 'POST'])
def signup():
    """ Create a new user and add to db.
        Afterwards, redirect to homepage.
        If form not valid, present form.
        If there are already a user with that username : flash message
    """
    search = request.args.get("q")
    if search:
        return do_search(search)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        bio = request.form.get('bio')
        try:
            new_user = User.register(username, email, password)
            new_user.bio = bio
            db.session.commit()
        except IntegrityError:
            flash('Username already taken', 'danger')
            return render_template('register.html')
        do_login(new_user)
        flash(f"Welcome {new_user.username}", "success")
        return redirect("/")
    else:
        return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    search = request.args.get("q")
    if search:
        return do_search(search)
    if request.method == 'POST':
        user = User.authenticate(
            request.form.get("username"),
            request.form.get("password")
        )
        if user:
            do_login(user)
            flash(f"Welcome {user.username}", "success")
            return redirect("/")
        else:
            flash("Invalid username or password", 'danger')
            return redirect("/")
    return render_template("/login.html")


@app.route("/logout", methods=["GET"])
def logout():
    do_logout()
    g.user = None
    flash("Logged out", "danger")
    return redirect("/")


@app.route("/recipe-post", methods=['GET', 'POST'])
def recipe_posts():
    search = request.args.get("q")
    if search:
        return do_search(search)
    if not g.user:
        flash("Please sign-in first", 'danger')
        return redirect("/login")

    if request.method == 'POST':
        title = request.form.get('recipe_title')
        ingredients = request.form.get('recipe_ingredients')
        instructions = request.form.get('recipe_instructions')
        photos = request.form.get('recipe_photos')
        recipe = User_Recipe_Post(
            created_by=g.user.username,
            recipe_title=title,
            recipe_ingredients=ingredients,
            recipe_instructions=instructions,
            recipe_image=photos
        )
        db.session.add(recipe)
        db.session.commit()
        return redirect(f"/recipe/{recipe.id}")
    return render_template("recipe_posts.html")


@app.route("/profile/<int:id>", methods=['GET', 'POST'])
def user_profile(id):
    search = request.args.get("q")
    if search:
        return do_search(search)
    user = User.query.get_or_404(id)
    liked_recipes = Like.query.filter(Like.user_id == id).all()
    user_posts = User_Recipe_Post.query.filter(User_Recipe_Post.created_by == user.username).all()
    following_ids = [u.id for u in user.followers]
    already_following = following_ids.count(g.user.id)
    return render_template(
        '/userProfile/user.html',
        user=user,
        liked_recipes=liked_recipes,
        user_posts=user_posts,
        already_following=already_following
    )


@app.route("/profile/<int:id>/liked_recipes", methods=['GET'])
def user_liked_recipes(id):
    search = request.args.get("q")
    if search:
        return do_search(search)
    user = User.query.get_or_404(id)
    liked_recipes = Like.query.filter(Like.user_id == user.id).all()
    recipe_ids = [l.external_id for l in liked_recipes]
    my_liked_recipes = SpoonacularAPI.get_recipe_info_bulk(recipe_ids)

    user_liked_ids =  [
        l.user_posted_recipe_post_id for l in Like.query.filter(Like.user_id == user.id, Like.external_id == None).all()
    ]
    user_posted_recipe_likes = User_Recipe_Post.query.filter(User_Recipe_Post.id.in_(user_liked_ids)).all()
    print(user_posted_recipe_likes)

    return render_template("/userProfile/user_liked_recipes.html", liked_recipes=my_liked_recipes, user=user, user_recipes=user_posted_recipe_likes)


@app.route("/profile/<int:id>/followers", methods=['GET'])
def user_followers(id):
    search = request.args.get("q")
    if search:
        return do_search(search)
    user = User.query.get_or_404(id)
    followers = user.followers
    return render_template("/userProfile/followers.html", followers=followers, user=user)


@app.route("/profile/<int:id>/following", methods=['GET', 'POST'])
def user_followings(id):
    search = request.args.get("q")
    if search:
        return do_search(search)
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        f = Follows(user_being_followed_id=id, user_following_id=g.user.id)
        db.session.add(f)
        db.session.commit()
        flash(f"Followed {user.username}", "success")
        return redirect(f"/profile/{id}")
    else:
        return render_template("/userProfile/following.html", user=user)


@app.route("/profile/<int:id>/unfollow", methods=['POST'])
def user_unfollow(id):
    user = User.query.get_or_404(id)
    f = Follows.query.filter(
        Follows.user_being_followed_id == id,
        Follows.user_following_id == g.user.id
    ).one()
    db.session.delete(f)
    db.session.commit()
    flash(f"Unfollowed {user.username}")
    return redirect(f"/profile/{id}")


@app.route("/profile/<int:user_id>/recipe/posts", methods=['GET'])
def get_user_posted_recipes(user_id):
    search = request.args.get("q")
    if search:
        return do_search(search)
    user = User.query.get_or_404(user_id)
    if user.username == "api":
        my_posts = User_Recipe_Post.query.filter(
            User_Recipe_Post.created_by == user.username
        ).all()
        recipe_ids = [r.id for r in my_posts]
        posts = SpoonacularAPI.get_recipe_info_bulk(recipe_ids)
        return render_template("/userProfile/my_posted_recipes.html", user=user, my_posts=posts)
    else:
        my_posts = User_Recipe_Post.query.filter(User_Recipe_Post.created_by == user.username).all()
        return render_template("/userProfile/my_posted_recipes.html", user=user, my_posts=my_posts)

def do_search(term):
    search_results = SpoonacularAPI.search_recipe(term)
    result_ids = [s['id'] for s in search_results['results']]
    if g.user:
        likes = Like.query.filter(Like.user_id == g.user.id).all()
        curr_user_liked_recipe_ids = [like.user_posted_recipe_post_id for like in likes]
        return render_template(
            "/recipes/search_results.html",
            results=search_results,
            search=term,
            liked_ids=curr_user_liked_recipe_ids
        )
    else:
        return render_template(
            "/recipes/search_results.html",
            results=search_results,
            search=term,
            already_liked=False
        )

@app.route("/", methods=['GET'])
def homepage():
    """ Page listing with holiday specials, breakfast, lunch, dinner recipes
        Can take a 'q' param in querystring to search recipes
    """
    search = request.args.get("q")
    if search:
        return do_search(search)
    breakfast = SpoonacularAPI.get_breakfast()
    breakfast_results = breakfast['results']
    image_base_uri = breakfast['baseUri']
    random_recipes = SpoonacularAPI.get_random_recipes()
    recipes = random_recipes['recipes']
    lunch = SpoonacularAPI.get_lunch()
    lunch_results = lunch['results']
    dinner = SpoonacularAPI.get_dinner()
    dinner_results = dinner['results']
    try:
        likes = Like.query.filter(Like.user_id == g.user.id).all()
        curr_user_liked_recipe_ids = [like.user_posted_recipe_post_id for like in likes] + [like.external_id for like in likes]

        return render_template(
            'home.html',
            recipes=recipes,
            breakfast=breakfast_results,
            imageUri=image_base_uri,
            lunch=lunch_results,
            dinner=dinner_results,
            liked_ids=curr_user_liked_recipe_ids
        )
    except:
        return render_template(
            "home.html",
            recipes=recipes,
            breakfast=breakfast_results,
            imageUri=image_base_uri,
            lunch=lunch_results,
            dinner=dinner_results
        )


@app.route("/recipe/<int:id>", methods=['GET'])
def get_recipe_details(id):
    search = request.args.get("q")
    if search:
        return do_search(search)
    if not g.user:
        flash("Please sign-in first", "danger")
        return redirect("/login")

    try:
        found_recipe = User_Recipe_Post.query.filter(
            User_Recipe_Post.id == id,
            User_Recipe_Post.created_by != "api"
        ).one()
        likes = Like.query.filter(Like.user_id == g.user.id).all()
        curr_user_liked_recipe_ids = [like.user_posted_recipe_post_id for like in likes]
        all_comments = Comment.query.filter(Comment.recipe_post_id == id).all()
        already_liked = curr_user_liked_recipe_ids.count(id) > 0
        return render_template(
            "/recipes/user_recipe_details.html",
            recipe=found_recipe,
            already_liked=already_liked,
            all_comments=all_comments,
            hashtags=[]
        )
    except Exception as e:
        print(e)
        dummy_api_user = User.query.get(1)
        dummy_api_user_posts = dummy_api_user.posts
        recipe = SpoonacularAPI.get_recipe_detail_by_id(id)

        if not dummy_api_user_posts.count(id) > 0:
            add_api_recipe_posts_to_dummyAPI_user(id, recipeObj=recipe)

        likes = Like.query.filter(Like.user_id == g.user.id).all()
        curr_user_liked_recipe_ids = [like.external_id for like in likes]
        already_liked = curr_user_liked_recipe_ids.count(id) > 0

        hashtags = recipe['dishTypes']
        all_comments = Comment.query.filter(Comment.external_id == id).all()

        ingredients_base_url = 'https://spoonacular.com/cdn/ingredients_100x100/'
        recipes_base_url = 'https://spoonacular.com/recipeImages/'
        similar_recipes = SpoonacularAPI.get_similar_recipe_by_id(id)

        return render_template(
            "/recipes/recipe_details.html",
            recipe=recipe,
            hashtags=hashtags,
            already_liked=already_liked,
            all_comments=all_comments,
            ingredients_base_url=ingredients_base_url,
            similar_recipes=similar_recipes,
            recipes_base_url=recipes_base_url
        )


@app.route("/recipe/<int:id>/like", methods=['POST'])
def like_recipe(id):
    if not g.user:
        flash("Sign in first", "danger")
        return redirect("/login")
    try:
        like = Like(user_id=g.user.id, user_posted_recipe_post_id=id)
        db.session.add(like)
        db.session.commit()
        flash("Added this recipe to your likes", "success")
        return redirect(f"/recipe/{id}")
    except Exception:
        db.session.rollback()
        like = Like(user_id=g.user.id, external_id=id)
        db.session.add(like)
        db.session.commit()
        flash("Added this recipe to your likes", "success")
        return redirect(f"/recipe/{id}")

@app.route("/recipe/<int:id>/unlike", methods=['POST'])
def unlike_recipe(id):
    if not g.user:
        flash("Sign in first", "danger")
        return redirect("/login")
    try:
        like = Like.query.filter(Like.user_posted_recipe_post_id == id).one()
        db.session.delete(like)
        db.session.commit()
        flash("Removed this recipe from your likes", "danger")
        return redirect(f"/recipe/{id}")
    except Exception:
        like = Like.query.filter(Like.external_id == id).one()
        db.session.delete(like)
        db.session.commit()
        flash("Removed this recipe from your likes", "danger")
        return redirect(f"/recipe/{id}")


@app.route("/recipe/<int:id>/comment", methods=['POST'])
def add_comment_to_recipe(id):
    if not g.user:
        flash("Sign in first", "danger")
        return redirect("/login")
    try:
        comment = Comment(
            created_by=g.user.username,
            recipe_post_id=id,
            comment=request.form.get("comment")
        )
        db.session.add(comment)
        db.session.commit()
        flash("Added comment", "success")
        return redirect(f"/recipe/{id}")
    except Exception:
        db.session.rollback()
        comment = Comment(
            created_by=g.user.username,
            external_id=id,
            comment=request.form.get("comment")
        )
        db.session.add(comment)
        db.session.commit()
        flash("Added comment", "success")
        return redirect(f"/recipe/{id}")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


def add_api_recipe_posts_to_dummyAPI_user(apiPostID, recipeObj):
    recipe_post = User_Recipe_Post(
        created_by="api",
        recipe_title = recipeObj['title'],
        recipe_ingredients = json.dumps(recipeObj['extendedIngredients']),
        recipe_instructions = recipeObj['instructions'] or "instructions",
        recipe_image=recipeObj['image'],
        external_id=apiPostID
    )
    db.session.merge(recipe_post)
    db.session.commit()

# setUp()
