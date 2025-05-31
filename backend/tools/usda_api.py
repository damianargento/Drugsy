from langchain.tools import tool
import requests
import os
import dotenv

dotenv.load_dotenv()

@tool
def query_usda_food_data(food_query: str) -> dict:
    """
    Makes a query to the USDA FoodData Central API to get nutritional information for a given food.
    """
    api_key = os.getenv("USDA_API_KEY")
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food_query}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["foods"]:
            food = data["foods"][0]
            result = {
                "description": food.get("description"),
                "fdcId": food.get("fdcId"),
                "dataType": food.get("dataType"),
                "brandOwner": food.get("brandOwner"),
                "ingredients": food.get("ingredients"),
                "nutrients": {
                    nutrient["name"]: nutrient["amount"]
                    for nutrient in food.get("foodNutrients", [])
                }
            }
        else:
            result = {"message": f"No matches found for '{food_query}'."}
    else:
        result = {"message": f"Error while consulting the USDA API: {response.status_code}"}

    print(f"[USDA Tool Response] Input: '{food_query}' → Output: {result}")
    return result
