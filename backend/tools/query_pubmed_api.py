from langchain.tools import tool
import requests
import xml.etree.ElementTree as ET

@tool
def query_pubmed_api(query: str, max_results: int = 3) -> str:
    """
    Searches PubMed for research articles related to the query (e.g., a drug).
    Returns the titles and summaries of the top articles.
    
    Parameters:
    - query: A search string (e.g., drug name or interaction topic).
    - max_results: Number of top articles to return (default is 3).
    """

    # Step 1: Search for relevant articles and get their PMIDs
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "tool": "Drugsy",
        "email": "drugsy@gmail.com"
    }
    print(search_params)
    search_response = requests.get(search_url, params=search_params)
    print(search_response)
    if search_response.status_code != 200:
        return f"PubMed search failed for '{query}'."

    id_list = search_response.json().get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return f"No PubMed articles found for '{query}'."

    # Step 2: Fetch details for the top articles using EFetch
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml",
        "tool": "Drugsy",
        "email": "drugsy@gmail.com"
    }
    print(fetch_params)

    fetch_response = requests.get(fetch_url, params=fetch_params)
    if fetch_response.status_code != 200:
        return f"Failed to fetch PubMed details for '{query}'."
    print(fetch_response)
    # Step 3: Parse the XML response
    root = ET.fromstring(fetch_response.content)
    articles = []
    
    for article in root.findall(".//PubmedArticle"):
        title_elem = article.find(".//ArticleTitle")
        abstract_elem = article.find(".//AbstractText")
        pmid_elem = article.find(".//PMID")
        title = title_elem.text if title_elem is not None else "No title found"
        abstract = abstract_elem.text if abstract_elem is not None else "No abstract found"
        pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
        articles.append(f"PMID: {pmid}\nTitle: {title}\nAbstract: {abstract}")

    return "\n\n".join(articles)
