from langchain.tools import tool
import requests
import xml.etree.ElementTree as ET
import logging
import os
import tempfile
import uuid
from typing import List, Dict, Any

# For text chunking
from langchain_text_splitters import RecursiveCharacterTextSplitter

# For embeddings
from sentence_transformers import SentenceTransformer

# For vector database
import chromadb

# For LLM integration - use existing Drugsy LLM
from langchain.prompts import ChatPromptTemplate
from models.llm import llm

# Constants
MAX_ARTICLES = 25  # Fetch 25 articles
CHUNK_SIZE = 500    # ~500 tokens per chunk
CHUNK_OVERLAP = 50  # 50 token overlap
TOP_K_RESULTS = 5   # Retrieve top 5 chunks

# Biomedical embedding model
EMBEDDING_MODEL = "pritamdeka/S-PubMedBert-MS-MARCO"  # Biomedical domain-specific model

class PubMedRAGPipeline:
    """RAG Pipeline for PubMed data retrieval and processing."""
    
    def __init__(self):
        """Initialize the RAG pipeline components."""
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            print(f"Initialized embedding model: {EMBEDDING_MODEL}")
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
            raise
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        
        # Initialize temporary vector database
        self.vector_db = None
        self._setup_vector_db()
    
    def _setup_vector_db(self):
        """Set up a new temporary vector database instance."""
        try:
            # Create a temporary directory for ChromaDB
            # This will be automatically cleaned up when the Python process exits
            temp_dir = tempfile.gettempdir()
            persist_dir = os.path.join(temp_dir, f"drugsy_chromadb_{uuid.uuid4().hex}")
            
            # Create a client with the new API format
            self.vector_db = chromadb.PersistentClient(path=persist_dir)
            
            # Create a new collection for this query
            self.collection = self.vector_db.create_collection(
                name="pubmed_abstracts",
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Initialized temporary vector database in {persist_dir}")
        except Exception as e:
            print(f"Failed to initialize vector database: {e}")
            raise
    
    def search_pubmed(self, query: str, max_results: int = MAX_ARTICLES) -> List[Dict[str, Any]]:
        """
        Search PubMed for articles related to the query, map PMIDs to PMC IDs,
        and retrieve full text when available.
        """
        print(f"Searching PubMed for: {query} (max results: {max_results})")
        
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
        
        try:
            search_response = requests.get(search_url, params=search_params)
            search_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"PubMed search failed: {e}")
            return []
        
        id_list = search_response.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            print(f"No PubMed articles found for '{query}'")
            return []
        
        print(f"Found {len(id_list)} PubMed articles")
        
        # Step 2: Map PMIDs to PMC IDs using elink.fcgi
        pmid_to_pmcid = {}
        elink_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
        elink_params = {
            "dbfrom": "pubmed",
            "db": "pmc",
            "id": ",".join(id_list),
            "retmode": "xml",
            "tool": "Drugsy",
            "email": "drugsy@gmail.com"
        }
        
        try:
            elink_response = requests.get(elink_url, params=elink_params)
            elink_response.raise_for_status()
            
            try:
                elink_root = ET.fromstring(elink_response.content)
                
                # Parse the elink response to map PMIDs to PMC IDs
                for link_set in elink_root.findall(".//LinkSet"):
                    try:
                        pmid_elem = link_set.find(".//IdList/Id")
                        if pmid_elem is not None:
                            pmid = pmid_elem.text
                            # Look for linked PMC IDs
                            link_set_db = link_set.findall(".//LinkSetDb")
                            if link_set_db:
                                for link_elem in link_set.findall(".//LinkSetDb/Link/Id"):
                                    if link_elem is not None and link_elem.text:
                                        pmcid = link_elem.text
                                        if pmid and pmcid:
                                            pmid_to_pmcid[pmid] = pmcid
                                            print(f"Found PMC ID {pmcid} for PMID {pmid}")
                    except Exception as parse_error:
                        print(f"Error parsing link set: {parse_error}")
                        continue
                
                print(f"Mapped {len(pmid_to_pmcid)} PMIDs to PMC IDs")
            except ET.ParseError as xml_error:
                print(f"XML parsing error in elink response: {xml_error}")
                # Continue with the process even if mapping fails
        except requests.exceptions.RequestException as req_error:
            print(f"Request error in elink API call: {req_error}")
            # Continue with the process even if mapping fails
        except Exception as e:
            print(f"Unexpected error mapping PMIDs to PMC IDs: {e}")
            # Continue with the process even if mapping fails
        
        # Step 3: Fetch details for the articles using EFetch
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
            "tool": "Drugsy",
            "email": "drugsy@gmail.com"
        }
        
        try:
            fetch_response = requests.get(fetch_url, params=fetch_params)
            fetch_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch PubMed details: {e}")
            return []
        
        # Step 4: Parse the XML response
        try:
            try:
                root = ET.fromstring(fetch_response.content)
                articles = []
                
                for article in root.findall(".//PubmedArticle"):
                    try:
                        # Extract article metadata
                        pmid_elem = article.find(".//PMID")
                        pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
                        
                        title_elem = article.find(".//ArticleTitle")
                        title = title_elem.text if title_elem is not None else "No title found"
                        
                        # Handle multiple AbstractText elements or nested structure
                        abstract = ""
                        abstract_elems = article.findall(".//AbstractText")
                        if abstract_elems:
                            for elem in abstract_elems:
                                try:
                                    # Check for labeled abstract sections
                                    label = elem.get("Label")
                                    if label:
                                        abstract += f"{label}: {elem.text}\n" if elem.text else ""
                                    else:
                                        abstract += f"{elem.text}\n" if elem.text else ""
                                except Exception as abstract_error:
                                    print(f"Error processing abstract element for PMID {pmid}: {abstract_error}")
                                    continue
                        else:
                            abstract = "No abstract found"
                        
                        # Extract publication year
                        year_elem = article.find(".//PubDate/Year")
                        year = year_elem.text if year_elem is not None else "Unknown year"
                        
                        # Extract journal name
                        journal_elem = article.find(".//Journal/Title")
                        journal = journal_elem.text if journal_elem is not None else "Unknown journal"
                        
                        # Create article data with abstract
                        article_data = {
                            "pmid": pmid,
                            "title": title,
                            "abstract": abstract.strip(),
                            "year": year,
                            "journal": journal,
                            "full_text": "",
                            "text_source": "AbstractOnly"  # Default to abstract only
                        }
                        
                        # Check if we have a PMC ID for this PMID
                        if pmid in pmid_to_pmcid:
                            try:
                                pmcid = pmid_to_pmcid[pmid]
                                article_data["pmcid"] = pmcid
                                
                                # Try to fetch full text from PMC
                                full_text = self._fetch_pmc_full_text(pmcid)
                                if full_text:
                                    article_data["full_text"] = full_text
                                    article_data["text_source"] = "FullTextFetched"
                                    print(f"Added full text for PMID {pmid} (PMC ID: {pmcid})")
                                else:
                                    article_data["text_source"] = "FullTextFailed"
                                    print(f"Failed to fetch full text for PMID {pmid} (PMC ID: {pmcid})")
                            except Exception as pmc_error:
                                print(f"Error processing PMC full text for PMID {pmid}: {pmc_error}")
                                article_data["text_source"] = "FullTextFailed"
                        
                        articles.append(article_data)
                    except Exception as article_error:
                        print(f"Error processing article: {article_error}")
                        continue
                
                print(f"Successfully parsed {len(articles)} articles")
                return articles
            except ET.ParseError as xml_error:
                print(f"XML parsing error in PubMed response: {xml_error}")
                return []
        except Exception as e:
            print(f"Unexpected error parsing PubMed response: {e}")
            return []
    
    def _fetch_pmc_full_text(self, pmcid: str) -> str:
        """
        Fetch full text from PMC using the PMC ID.
        
        This method retrieves the full article text from PubMed Central,
        extracting paragraph content, headings, and table captions.
        Figure captions are preserved as text, but images are ignored.
        
        Args:
            pmcid: The PubMed Central ID of the article
            
        Returns:
            A string containing the full article text, or an empty string if retrieval fails
        """
        print(f"Fetching full text for PMC ID: {pmcid}")
        
        # Use efetch to get the full text XML
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pmc",
            "id": pmcid,
            "retmode": "xml",
            "tool": "Drugsy",
            "email": "drugsy@gmail.com"
        }
        
        try:
            fetch_response = requests.get(fetch_url, params=fetch_params)
            fetch_response.raise_for_status()
            
            # Parse the XML response
            try:
                root = ET.fromstring(fetch_response.content)
                
                # Extract all body sections
                full_text = ""
                
                # Process all body elements (there might be multiple in some cases)
                body_elements = root.findall(".//body")
                if not body_elements:
                    print(f"No body elements found in PMC ID {pmcid} XML response")
                    return ""
                    
                for body in body_elements:
                    try:
                        # Extract paragraphs
                        for p in body.findall(".//p"):
                            if p.text:
                                full_text += p.text.strip() + "\n\n"
                            # Get any additional text within the paragraph
                            for child in p:
                                if child.tail:
                                    full_text += child.tail.strip() + " "
                            full_text += "\n"
                        
                        # Extract section titles/headings
                        for title in body.findall(".//title"):
                            if title.text:
                                full_text += title.text.strip() + "\n\n"
                        
                        # Extract table captions
                        for caption in body.findall(".//table-wrap/caption"):
                            if caption.text:
                                full_text += "Table Caption: " + caption.text.strip() + "\n\n"
                        
                        # Extract figure captions (but not the figures themselves)
                        for fig_caption in body.findall(".//fig/caption"):
                            if fig_caption.text:
                                full_text += "Figure Caption: " + fig_caption.text.strip() + "\n\n"
                    except Exception as inner_e:
                        print(f"Error processing body element in PMC ID {pmcid}: {inner_e}")
                        # Continue with other body elements if available
                
                # Clean up extra whitespace and newlines
                full_text = "\n".join([line.strip() for line in full_text.split("\n") if line.strip()])
                
                if full_text:
                    print(f"Successfully retrieved full text for PMC ID {pmcid} ({len(full_text)} characters)")
                    return full_text
                else:
                    print(f"No full text content found for PMC ID {pmcid}")
                    return ""
            except ET.ParseError as xml_error:
                print(f"XML parsing error for PMC ID {pmcid}: {xml_error}")
                return ""
                
        except requests.exceptions.RequestException as req_error:
            print(f"Request error fetching PMC full text for {pmcid}: {req_error}")
            return ""
        except Exception as e:
            print(f"Unexpected error fetching PMC full text for {pmcid}: {e}")
            return ""
    
    def chunk_abstracts(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split article content (abstract and full text when available) into smaller chunks for better processing."""
        if not articles:
            return []
        
        chunked_data = []
        for article in articles:
            # Prepare the text to be chunked, including full text if available
            base_text = f"PMID: {article['pmid']}\nTitle: {article['title']}\nJournal: {article['journal']} ({article['year']})\nAbstract:\n{article['abstract']}"
            
            # If full text is available, add it to the text
            if article.get('full_text') and article.get('text_source') == "FullTextFetched":
                text = f"{base_text}\n\nFull Text:\n{article['full_text']}"
                source_type = "PubMed+PMC"
                print(f"Processing article {article['pmid']} with full text ({len(article['full_text'])} chars)")
            else:
                text = base_text
                source_type = "PubMed"
                print(f"Processing article {article['pmid']} with abstract only")
            
            # Split the text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create metadata for each chunk
            for i, chunk in enumerate(chunks):
                chunked_data.append({
                    "text": chunk,
                    "metadata": {
                        "pmid": article["pmid"],
                        "title": article["title"],
                        "chunk_id": f"{article['pmid']}-{i}",
                        "source": source_type,
                        "text_source": article.get("text_source", "AbstractOnly")
                    }
                })
        
        print(f"Created {len(chunked_data)} chunks from {len(articles)} articles")
        return chunked_data
    
    def embed_and_store(self, chunks: List[Dict[str, Any]]):
        """Generate embeddings for chunks and store them in the vector database."""
        if not chunks:
            return
        
        # Reset vector database for new query
        self._setup_vector_db()
        
        # Prepare data for vector database
        ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Generate embeddings
        try:
            embeddings = self.embedding_model.encode(texts)
            
            # Add to vector database
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
            
            print(f"Added {len(chunks)} embedded chunks to vector database")
        except Exception as e:
            print(f"Failed to embed or store chunks: {e}")
            raise
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = TOP_K_RESULTS) -> List[str]:
        """Retrieve the most relevant chunks for a given query."""
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Query the vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Extract the documents
            if results and "documents" in results and results["documents"]:
                chunks = results["documents"][0]  # First query result
                print(f"Retrieved {len(chunks)} relevant chunks")
                return chunks
            else:
                print("No relevant chunks found")
                return []
                
        except Exception as e:
            print(f"Failed to retrieve relevant chunks: {e}")
            return []
    
    def construct_prompt(self, query: str, chunks: List[str]) -> str:
        """Construct a prompt for the LLM with system instruction, chunks, and query."""
        # Format the context by joining all chunks with separators
        context = "\n\n---\n\n".join(chunks)
        
        # Log the chunks being used in the prompt
        print(f"Using {len(chunks)} chunks in prompt")
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1} (first 100 chars): {chunk[:100]}...")
        
        # Create a prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a medical assistant AI that provides information based ONLY on the PubMed research abstracts provided below. 
            Do not use any other knowledge or make up information. 
            If the provided abstracts don't contain enough information to answer the question, say so clearly.
            Always cite the PMIDs of the articles you reference in your answer.
            Format your response in a clear, concise manner suitable for medical professionals.
            
            PUBMED ABSTRACTS:
            {context}
            """),
            ("human", "{query}")
        ])
        
        # Format the prompt
        prompt = prompt_template.format(context=context, query=query)
        return prompt
    
    def query_llm(self, prompt: str) -> str:
        """Query the LLM with the constructed prompt."""
        try:
            # Use the existing Drugsy LLM (Gemini)
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Failed to query LLM: {e}")
            return f"Error querying LLM: {str(e)}"
    
    def run_pipeline(self, query: str) -> str:
        """Execute the complete RAG pipeline end-to-end."""
        try:
            # Step 1: Search PubMed and get articles with full text when available
            print(f"Step 1: Searching PubMed for '{query}'")
            articles = self.search_pubmed(query, MAX_ARTICLES)
            print(f"Found {len(articles)} articles for '{query}'")
            if not articles:
                print(f"No PubMed articles found for '{query}'")
                return f"No PubMed articles found for '{query}'."
            
            # Log article sources
            full_text_count = sum(1 for article in articles if article.get('text_source') == 'FullTextFetched')
            abstract_only_count = sum(1 for article in articles if article.get('text_source') == 'AbstractOnly')
            failed_full_text_count = sum(1 for article in articles if article.get('text_source') == 'FullTextFailed')
            
            print(f"Article sources: {full_text_count} with full text, {abstract_only_count} with abstract only, {failed_full_text_count} failed full text retrieval")
            
            # Step 2: Chunk the articles (abstracts + full text when available)
            print(f"Step 2: Chunking {len(articles)} articles (abstracts + full text when available)")
            chunks = self.chunk_abstracts(articles)
            print(f"Created {len(chunks)} chunks from articles")
            
            # Step 3: Embed and store chunks
            print(f"Step 3: Embedding and storing chunks")
            self.embed_and_store(chunks)
            print(f"Chunks embedded and stored in vector DB")
            
            # Step 4: Retrieve relevant chunks for the query
            print(f"Step 4: Retrieving relevant chunks for '{query}'")
            relevant_chunks = self.retrieve_relevant_chunks(query, TOP_K_RESULTS)
            print(f"Retrieved {len(relevant_chunks)} relevant chunks")
            if not relevant_chunks:
                print(f"No relevant chunks found for '{query}'")
                return f"Could not find relevant information for '{query}' in the retrieved articles."
            
            # Step 5: Construct prompt with retrieved chunks
            print(f"Step 5: Constructing prompt with retrieved chunks")
            prompt = self.construct_prompt(query, relevant_chunks)
            
            # Log the prompt being sent to the LLM
            print(f"Prompt for LLM (first 200 chars): {prompt[:200]}...")
            
            # Step 6: Query LLM and get response
            print(f"Step 6: Querying LLM")
            response = self.query_llm(prompt)
            print(f"LLM response received (first 200 chars): {response[:200]}...")
            
            return response
            
        except Exception as e:
            print(f"Pipeline execution failed: {e}")
            return f"An error occurred while processing your query: {str(e)}"

# Initialize the RAG pipeline as a global instance
_rag_pipeline = None

def get_rag_pipeline() -> PubMedRAGPipeline:
    """Get or create the RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        try:
            _rag_pipeline = PubMedRAGPipeline()
        except Exception as e:
            print(f"Failed to initialize RAG pipeline: {e}")
            raise
    return _rag_pipeline

@tool
def query_pubmed_api(query: str) -> str:
    """
    Searches PubMed for research articles related to the query (e.g., a drug),
    processes the abstracts through a RAG pipeline, and returns a comprehensive answer.
    
    Parameters:
    - query: A search string (e.g., drug name, medical condition, or specific question).
    """
    import sys
    sys.stderr.write(f"\n\n*** PUBMED TOOL CALLED: {query} ***\n\n")
    sys.stderr.flush()
    try:
        # Get the RAG pipeline instance
        print(f"Starting PubMed RAG pipeline for query: {query}")
        pipeline = get_rag_pipeline()
        print("Pipeline initialized successfully")
        
        # Run the complete pipeline
        print("Running pipeline...")
        result = pipeline.run_pipeline(query)
        
        # Log the result directly to file
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("/Users/damianargento/Desktop/Drugsy/backend/pubmed_tool_results.log", "a") as f:
            f.write(f"\n[{timestamp}] RESULT (first 200 chars): {result[:200]}...\n")
            
        print(f"Pipeline completed with result: {result[:100]}..." if result else "Pipeline returned empty result")
        
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in query_pubmed_api: {e}")
        print(f"Error details:\n{error_details}")
        
        return f"An error occurred while processing your query: {str(e)}"
