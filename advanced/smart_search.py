import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import sqlite3
import threading
import concurrent.futures
from typing import List, Dict, Any
import time
import json

class OllamaWebCrawlerService:
    def __init__(self, base_url: str, model: str = "llama2", max_depth: int = 1):
        """
        Initialize the Ollama-enhanced web crawler service
        
        :param base_url: Starting website portal URL
        :param model: Ollama LLM model to use
        :param max_depth: Maximum depth of crawling
        """
        # Ollama Configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = model
        
        # Crawler Configuration
        self.base_url = base_url
        self.base_domain = urllib.parse.urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls = set()
        self.db_lock = threading.Lock()
        
        # Initialize SQLite database
        self.conn = sqlite3.connect('ollama_web_crawler_data.db', 
                                    check_same_thread=False)
        self.create_database()
    
    def create_database(self):
        """Create SQLite database schema"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_pages (
                url TEXT PRIMARY KEY,
                content TEXT,
                title TEXT,
                images TEXT,
                metadata TEXT
            )
        ''')
        self.conn.commit()
    
    def ollama_request(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Send request to local Ollama LLM
        
        :param prompt: Input prompt
        :param max_tokens: Maximum response tokens
        :return: LLM generated response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                self.ollama_url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"Ollama API Error: {response.text}")
                return ""
        
        except Exception as e:
            print(f"Ollama request error: {e}")
            return ""
    
    def sanitize_url(self, url: str) -> str:
        """Sanitize and normalize URL"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return urllib.parse.urljoin(base_url, parsed_url.path)
        except Exception:
            return url
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid, within the same domain and has not already been visited"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            return (
                parsed_url.scheme in ['http', 'https'] and
                parsed_url.netloc == self.base_domain and  # Check if same domain
                url not in self.visited_urls
            )
        except Exception:
            return False
    
    def extract_content(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract relevant content from BeautifulSoup object"""
        # Extract text content
        text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'div'])])
        
        # Extract images
        images = [img.get('src') for img in soup.find_all('img') if img.get('src')]
        images = [urllib.parse.urljoin(url, img) for img in images]
        
        # Extract title
        title = soup.title.string if soup.title else "No Title"
        
        return {
            'url': url,
            'content': text_content,
            'title': title,
            'images': ','.join(images)
        }
    
    def crawl_page(self, url: str, current_depth: int = 0):
        """Crawl a single page and store its data"""
        if current_depth > self.max_depth or not self.is_valid_url(url):
            return
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise exception for bad status code
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and store page content
            page_data = self.extract_content(url, soup)
            
            # Thread-safe database insertion
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO web_pages 
                    (url, content, title, images) 
                    VALUES (?, ?, ?, ?)
                ''', (
                    page_data['url'], 
                    page_data['content'], 
                    page_data['title'], 
                    page_data['images']
                ))
                self.conn.commit()
            
            self.visited_urls.add(url)
            
            # Find and crawl links if depth allows
            if current_depth < self.max_depth:
                links = [
                    urllib.parse.urljoin(url, link.get('href')) 
                    for link in soup.find_all('a', href=True)
                ]
                
                # Use ThreadPoolExecutor for concurrent crawling
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [
                        executor.submit(self.crawl_page, link, current_depth + 1) 
                        for link in links if self.is_valid_url(link)
                    ]
                    concurrent.futures.wait(futures)
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    
    def start_crawling(self):
        """Start the web crawling process"""
        print(f"Starting crawl for {self.base_url}")
        start_time = time.time()
        self.crawl_page(self.base_url)
        end_time = time.time()
        print(f"Crawling completed in {end_time - start_time:.2f} seconds")
        print(f"Total unique URLs crawled: {len(self.visited_urls)}")
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Perform semantic search using local Ollama LLM
        
        :param query: Natural language search query
        :param limit: Maximum number of results
        :return: List of matching search results
        """
        try:
            # Use Ollama to understand query intent
            intent_prompt = f"""
            Analyze the following search query and extract key semantic search terms:
            Query: {query}
            
            Provide a comma-separated list of key search terms that capture the query's intent.
            """
            
            semantic_terms = self.ollama_request(intent_prompt, max_tokens=100)
            
            # Perform database search
            cursor = self.conn.cursor()
            search_conditions = ' OR '.join([
                f"content LIKE '%{term.strip()}%'" 
                for term in semantic_terms.split(',') 
                if term.strip()
            ])
            
            cursor.execute(f'''
                SELECT url, title, content, images 
                FROM web_pages 
                WHERE {search_conditions}
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            # Contextualize results using Ollama
            contextualized_results = []
            for result in results:
                context_prompt = f"""
                Evaluate the relevance of this content to the query: "{query}"
                
                Content Details:
                Title: {result[1]}
                Content Snippet: {result[2][:500]}
                
                Provide a brief relevance assessment and key insights.
                """
                
                context_response = self.ollama_request(context_prompt, max_tokens=200)
                
                contextualized_results.append({
                    'url': result[0],
                    'title': result[1],
                    'content': result[2],
                    'images': result[3].split(',') if result[3] else [],
                    'relevance': context_response
                })
            
            return contextualized_results
        
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []
    
    def interactive_chat(self, query: str) -> str:
        """
        Use local Ollama LLM to provide natural language interaction
        
        :param query: User's natural language query
        :return: Detailed LLM-generated response
        """
        # Perform semantic search first
        search_results = self.semantic_search(query)
        
        # Prepare context for LLM
        context = "\n\n".join([
            f"Source: {result['url']}\nTitle: {result['title']}\nContent: {result['content'][:300]}..."
            for result in search_results
        ])
        
        # Generate comprehensive response
        try:
            chat_prompt = f"""
            User Query: {query}
            
            Contextual Search Results:
            {context}
            
            Please provide a comprehensive, natural language response 
            that directly addresses the user's query using the 
            contextual information from the web crawl. 
            
            Include:
            1. Direct answer to the query
            2. Key insights from crawled sources
            3. Relevant source URLs
            
            Format the response in a clear, conversational manner.
            """
            
            chat_response = self.ollama_request(chat_prompt, max_tokens=1000)
            return chat_response
        
        except Exception as e:
            return f"Error generating response: {e}"
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    # Interactive Demo
    print("=" * 50)
    print("Ollama-Enhanced Web Crawler Search Service")
    print("=" * 50)
    
    # Available Ollama Models
    available_models = [
        "llama3.1", 
        "mistral", 
        "neural-chat", 
        "openhermes", 
        "zephyr"
    ]
    
    # Display available models
    print("Available Ollama Models:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")
    
    # Select model
    model_choice = int(input("Select model number: "))
    selected_model = available_models[model_choice - 1]
    
    # Get base URL to crawl
    base_url = input("Enter base URL to crawl (e.g., https://www.example.com): ")
    
    # Initialize crawler
    crawler = OllamaWebCrawlerService(
        base_url=base_url, 
        model=selected_model,
        max_depth=1
    )
    
    # Start crawling
    crawler.start_crawling()
    
    # Interactive chat loop
    while True:
        print("\nMenu:")
        print("1. Ask a Question")
        print("2. Perform Semantic Search")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            query = input("Ask your question (or type 'exit' to return): ")
            if query.lower() == 'exit':
                continue
            
            # Generate conversational response
            response = crawler.interactive_chat(query)
            print("\n--- Ollama LLM Response ---")
            print(response)
        
        elif choice == '2':
            query = input("Enter search query (or type 'exit' to return): ")
            if query.lower() == 'exit':
                continue
            
            # Perform semantic search
            results = crawler.semantic_search(query)
            
            print("\n--- Search Results ---")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"URL: {result['url']}")
                print(f"Title: {result['title']}")
                print(f"Snippet: {result['content'][:300]}...")
                print(f"Relevance: {result.get('relevance', 'N/A')}")
        
        elif choice == '3':
            print("Exiting Ollama Web Crawler Search Service. Goodbye!")
            crawler.close()
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
