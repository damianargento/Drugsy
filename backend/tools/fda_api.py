from langchain.tools import tool
import requests

@tool
def query_fda_api(search_query: str) -> str:
    """Makes a query to the FDA API to get information about a drug.
    
    ARGS:
        search_query: A formatted query string that will be appended to the FDA API URL.
                     Must be in the format 'search=parameter:value' (without quotes).
                     For example: 'search=active_ingredient:omeprazole' or 'search=active_ingredient:"omeprazole 20 mg"'
    
    EXAMPLES:
        - For omeprazole: 'search=active_ingredient:omeprazole'
        - For ibuprofen: 'search=active_ingredient:ibuprofen'
        - For active ingredient: 'search=active_ingredient:"omeprazole 20 mg"'
        - For brand name Advil: 'search=brand_name:advil'
        - For multiple terms: 'search=active_ingredient:omeprazole+AND+brand_name:prilosec'
    
    NOTES:
        - Users may make mistakes in drug names or ask in different languages
        - Translate non-English drug names to English before querying
        - Fix typos in drug names before querying
        - If unsure about a drug name, ask the user to confirm
    
    RETURNS:
        A dictionary with the following keys:
        - product
        - ingredient_searched
        - active_ingredient
        - interactions
        - indications_and_usage
        - dosage_and_administration
        - warnings
        - do_not_use
    """
    url = f'https://api.fda.gov/drug/label.json?{search_query}'
    response = requests.get(url)
    print(response)
    print(url)
    if response.status_code == 200 and "results" in response.json():
        data = response.json()["results"][0]
        print(data)
        return {
            "product": data.get("spl_product_data_elements", [None])[0],
            "ingredient_searched": search_query,
            "active_ingredients": data.get("active_ingredient", [None])[0],
            "interactions": data.get("drug_interactions", [None])[0],
            "indications_and_usage": data.get("indications_and_usage", [None])[0],
            "dosage_and_administration": data.get("dosage_and_administration", [None])[0],
            "warnings": data.get("warnings", [None])[0],
            "do_not_use": data.get("do_not_use", [None])[0]
        }
    else:
        return f"No data found for {search_query}"
