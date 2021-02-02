# allRecipes
- https://evening-anchorage-37505.herokuapp.com/
- Search between numerous recipes, or even post your own!
- Once registering an account, users can post, like, and comment on recipes.
- Users can also follow other users' and see which recipes they posted and liked. 
- Users can also search for recipes.

  ## Requirements
  1. Install required packages `pip install -r requirements.txt`
  2. You need to have postgresql installed for this to work.
    - After installing postgresql, create a database named recipes.
  3. From the same directory where `app.py` resides, run the flask app with `flask run`
  4. After the app starts, run the `initializeDB.py` file to initialize the tables.
  
  ## API Used
  * [spoonacular API](https://spoonacular.com/food-api)

  ## Database Schema
  [DB Schema Image](https://i.imgur.com/d2FMj50.png)
  You can also see the schema [here](https://app.quickdatabasediagrams.com/#/d/v7Eozr)

  ## How to Run Tests
  - You may see two test files `test_user_model.py` and `test_user_recipe_post.py`
  - Prior to running these tests, make sure you create a database named 'recipe_test'
  - Run the tests with the following command `python -m unittest NAME_OF_TEST_FILE.py`
  
  ## Technologies Utilized
  - flask
  - python
  - javaScript
  - Jinja
  - SQLAlchemy
  - Postgresql 
  - HTML
  - CSS/Bootstrap
 
