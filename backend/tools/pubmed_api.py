from langchain.tools import tool
import requests
import json

@tool
def query_pubmed_api(search_query: str) -> str:
    """Makes a query to the PubMed API to get scientific articles about drugs and their interactions.
    
    ARGS:
        search_query: A search term or phrase to find relevant medical articles.
                     For example: 'omeprazole food interactions'
    
    EXAMPLES:
        - 'omeprazole food interactions'
        - 'ibuprofen mechanism of action'
        - 'metformin diabetes treatment'
        - 'drug interactions grapefruit'
    
    RETURNS:
        A list of the top 3 most relevant articles with their titles, authors, 
        publication dates, journals, and abstracts.
    """
    # Base URL for the PubMed API (E-utilities)
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # Step 1: Search for articles matching the query
    search_url = f"{base_url}/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": search_query,
        "retmode": "json",
        "retmax": 3  # Limit to top 3 results
    }
    
    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code != 200:
        return f"Error searching PubMed: {search_response.status_code}"
    
    search_data = search_response.json()
    id_list = search_data.get('esearchresult', {}).get('idlist', [])
    
    if not id_list:
        return "No articles found for this query."
    
    # Step 2: Fetch details for the found article IDs
    fetch_url = f"{base_url}/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }
    
    fetch_response = requests.get(fetch_url, params=fetch_params)
    if fetch_response.status_code != 200:
        return f"Error fetching article details: {fetch_response.status_code}"
    
    # Parse the XML response to extract article details
    # This is a simplified version - in a real implementation, you would use
    # a proper XML parser to extract structured data
    
    # For this example, we'll return a simplified response
    articles = []
    
    for article_id in id_list:
        summary_url = f"{base_url}/esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": article_id,
            "retmode": "json"
        }
        
        summary_response = requests.get(summary_url, params=summary_params)
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            article_data = summary_data.get('result', {}).get(article_id, {})
            
            title = article_data.get('title', 'No title available')
            authors = ', '.join([author.get('name', '') for author in article_data.get('authors', [])])
            pub_date = article_data.get('pubdate', 'No date available')
            journal = article_data.get('fulljournalname', 'No journal available')
            
            # Get abstract
            abstract_url = f"{base_url}/efetch.fcgi"
            abstract_params = {
                "db": "pubmed",
                "id": article_id,
                "retmode": "xml"
            }
            
            abstract_response = requests.get(abstract_url, params=abstract_params)
            abstract = "Abstract not available"
            
            if abstract_response.status_code == 200:
                # Simple string search for abstract in XML
                # In a real implementation, use proper XML parsing
                abstract_text = abstract_response.text
                if "<AbstractText>" in abstract_text and "</AbstractText>" in abstract_text:
                    start = abstract_text.find("<AbstractText>") + len("<AbstractText>")
                    end = abstract_text.find("</AbstractText>")
                    abstract = abstract_text[start:end].strip()
            
            articles.append({
                "pmid": article_id,
                "title": title,
                "authors": authors,
                "publication_date": pub_date,
                "journal": journal,
                "abstract": abstract
            })
    
    # Format the results
    if not articles:
        return "Could not retrieve article details."
    print(articles)
    result = "PubMed Search Results:\n\n"
    for i, article in enumerate(articles, 1):
        result += f"Article {i}:\n"
        result += f"Title: {article['title']}\n"
        result += f"Authors: {article['authors']}\n"
        result += f"Journal: {article['journal']}\n"
        result += f"Publication Date: {article['publication_date']}\n"
        result += f"PMID: {article['pmid']}\n"
        result += f"Abstract: {article['abstract']}\n\n"
    
    return result
