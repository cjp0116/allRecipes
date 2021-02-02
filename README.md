# allRecipes
- https://evening-anchorage-37505.herokuapp.com/
- Search between numerous recipes, or even post your own!
- You may like, comment on recipes.
- Follow other users' see what kind of recipes they posted! 
- Some routes requires authentication. So register first

  ## Requirements
  1. Install required packages `pip install -r requirements.txt`
  2. You need to have postgresql installed for this to work.
    - After installing postgresql, create a database named recipes.
  3. Under `app.py` line 395 uncomment the `setUp()` to initialize the tables for the recipes db. You can comment it out after (You only need to do it once for initialization). 
  4. From the same directory where `app.py` resides, run the flask app with `flask run`
  
  ## API Used
  * [spoonacular API](https://spoonacular.com/food-api)

  ## Database Schema
  [DB Schema Image](https://i.imgur.com/d2FMj50.png)
  You can also see the schema [here](https://app.quickdatabasediagrams.com/#/d/v7Eozr)

