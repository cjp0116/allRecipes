import requests
import json

querystring = {"targetCalories": "2000", "timeFrame": "day"}

headers = {
    'x-rapidapi-key': "cf4c86dd99mshceb73bd554abf6ep10eabdjsn260fb4cd9936",
    'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
}

# response = requests.request("GET", url, headers=headers, params=querystring, verify=False)


class SpoonacularAPI:
    @classmethod
    def make_request(cls, querystring, method='GET'):
        BASE_URL = 'https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes'
        res = requests.request(method, BASE_URL,  headers=headers)
        return json.loads(res.text)

    @classmethod
    def get_random_recipes(cls):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/random"
        querystring = {"number": "10",
                       "limitLicense": "false", "tags": "lunch"}
        res = requests.request('GET', url, headers=headers,
                               params=querystring)
        return json.loads(res.text)

    @classmethod
    def get_breakfast(cls):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"
        querystring = {"query": "breakfast", "number": "10",
                       "offset": "0", "type": "breakfast"}
        res = requests.request('GET', url, headers=headers,
                               params=querystring)
        return json.loads(res.text)

    @classmethod
    def get_lunch(cls):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"
        querystring = {"query": "lunch", "number": "10",
                       "offset": "0", "type": "lunch"}
        res = requests.request('GET', url, headers=headers,
                               params=querystring)
        return json.loads(res.text)

    @classmethod
    def get_dinner(cls):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"
        querystring = {"query": "dinner", "number": "10",
                       "offset": "0", "type": "dinner"}
        res = requests.request('GET', url, headers=headers,
                               params=querystring)
        return json.loads(res.text)

    @classmethod
    def get_recipe_detail_by_id(cls, id):
        url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id}/information"
        res = requests.request('GET', url, headers=headers) 
        return json.loads(res.text)

    @classmethod
    def get_similar_recipe_by_id(cls, id):
        url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id}/similar"
        res = requests.get(url, headers=headers, params={
                           "number": "4"})
        return json.loads(res.text)

    @classmethod
    def get_recipe_info_bulk(cls, ids):
        if not ids:
            return []
        qString = ""
        for id in ids:
            if id:
                qString += str(id) + ","
        querystring = {"ids": qString[:-1]}
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/informationBulk"
        res = requests.request('GET', url, headers=headers,
                               params=querystring)
        return json.loads(res.text)

    @classmethod
    def search_recipe(cls, q):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"
        querystring = {
            "query" : q,
            "type" : "main course",
            "number" : "28"
        }
        res = requests.request("GET", url, headers=headers, params=querystring)
        return json.loads(res.text)