from langchain.tools import tool
import requests
import os
import dotenv

dotenv.load_dotenv()

@tool
def query_usda_food_data(food_query: str) -> dict:
    """
    Makes a query to the USDA FoodData Central API to get nutritional information for a given food.

    Parameters:
        food_query (str): Name of the food to search for (in English).

    Examples:
        - "avocado"
        - "chicken breast"
        - "whole milk"

    Notes:
        - The search is performed in English.
        - If the food name contains typos or is in another language, try correcting it or translating it before making the query.
        - If the food is not found, a message indicating that no results were found is returned.

    Returns:
        dict: Nutritional information for the found food.
    """
    api_key = os.getenv("USDA_API_KEY")
    print(api_key, "api_key")
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food_query}"
    headers = {"Content-Type": "application/json"}
    print(search_url, "search_url")
    response = requests.get(search_url, headers=headers)
    print(response.json(), "response")
    if response.status_code == 200:
        data = response.json()
        if data["foods"]:
            food = data["foods"][0]
            return {
                "description": food.get("description"),
                "fdcId": food.get("fdcId"),
                "dataType": food.get("dataType"),
                "brandOwner": food.get("brandOwner"),
                "ingredients": food.get("ingredients"),
                "nutrients": {nutrient["name"]: nutrient["amount"] for nutrient in food.get("foodNutrients", [])}
            }
        else:
            return {"message": f"No matches found for '{food_query}'."}
    else:
        return {"message": f"Error while consulting the USDA API: {response.status_code}"}
