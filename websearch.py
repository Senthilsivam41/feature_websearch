import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import re
import time
from typing import Dict, List

class WebScraper:
    """
    A web scraper that can crawl all pages of a given portal and store their content.
    """
    def __init__(self, start_url: str, max_depth: int = 5, request_timeout: int = 3, delay: float = 0.1, user_agent: str = None):
        """
        Initializes the WebScraper.

        Args:
            start_url: The initial URL of the portal to start scraping from.
            max_depth: The maximum depth to crawl.
            request_timeout: Timeout for HTTP requests in seconds.
            delay: Time to wait between requests to avoid overloading the server.
            user_agent: Custom user agent string for requests.
        """
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.visited = set()
        self.queue = deque([(start_url, 0)])  # (URL, depth)
        self.scraped_data: Dict[str, str] = {}  # URL: Content (text)
        self.max_depth = max_depth
        self.request_timeout = request_timeout
        self.delay = delay
        self.headers = {'User-Agent': user_agent or 'ComplexWebScraper/1.0'}

    def _get_page_content(self, url: str) -> str | None:
        """
        Fetches the content of a single web page.

        Args:
            url: The URL of the page.

        Returns:
            The text content of the page, or None if an error occurs.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.request_timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _extract_links(self, html_content: str, current_url: str) -> List[str]:
        """
        Extracts all valid links from the HTML content of a page.

        Args:
            html_content: The HTML content of the page.
            current_url: The URL of the current page to resolve relative links.

        Returns:
            A list of absolute URLs found on the page that belong to the target domain.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            absolute_url = urljoin(current_url, href)
            if urlparse(absolute_url).netloc == self.domain and absolute_url not in self.visited:
                links.append(absolute_url)
        return links

    def scrape_page(self, url: str) -> str | None:
        """
        Scrapes the text content from a given URL.

        Args:
            url: The URL to scrape.

        Returns:
            The extracted text content, or None if an error occurs.
        """
        content = self._get_page_content(url)
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text, break into lines and remove leading/trailing whitespace on each
            text = ('\n'.join(soup.stripped_strings))
            return text
        return None

    def crawl(self):
        """
        Starts the crawling process from the initial URL.
        """
        print(f"Starting crawl from: {self.start_url}")
        while self.queue:
            current_url, depth = self.queue.popleft()

            if current_url in self.visited or depth > self.max_depth:
                continue

            print(f"Crawling: {current_url} (Depth: {depth})")
            self.visited.add(current_url)
            time.sleep(self.delay)  # Be respectful to the server

            page_content = self._get_page_content(current_url)
            if page_content:
                text_content = self.scrape_page(current_url)
                if text_content:
                    self.scraped_data[current_url] = text_content

                if depth < self.max_depth:
                    links = self._extract_links(page_content, current_url)
                    for link in links:
                        if link not in self.visited:
                            self.queue.append((link, depth + 1))
            else:
                print(f"Failed to retrieve content for: {current_url}")

        print(f"Crawling finished. Found {len(self.scraped_data)} pages.")

class SearchEngine:
    """
    A simple search engine that allows searching through the scrapped content.
    """
    def __init__(self, scraped_data: Dict[str, str]):
        """
        Initializes the SearchEngine.

        Args:
            scraped_data: A dictionary where keys are URLs and values are the text content.
        """
        self.data = scraped_data

    def search(self, query: str, case_sensitive: bool = False) -> Dict[str, str]:
        """
        Searches for the given query in the scrapped content.

        Args:
            query: The search term.
            case_sensitive: Whether the search should be case-sensitive.

        Returns:
            A dictionary where keys are matching URLs and values are snippets of the content
            where the query was found.
        """
        results = {}
        if not case_sensitive:
            query = query.lower()
        for url, content in self.data.items():
            if not case_sensitive:
                content_lower = content.lower()
                if query in content_lower:
                    # Find the first occurrence and extract a snippet
                    start_index = content_lower.find(query)
                    end_index = start_index + len(query)
                    snippet_start = max(0, start_index - 50)
                    snippet_end = min(len(content), end_index + 100)
                    snippet = f"...{content[snippet_start:snippet_end]}..."
                    results[url] = snippet
            else:
                if query in content:
                    start_index = content.find(query)
                    end_index = start_index + len(query)
                    snippet_start = max(0, start_index - 50)
                    snippet_end = min(len(content), end_index + 100)
                    snippet = f"...{content[snippet_start:snippet_end]}..."
                    results[url] = snippet
        return results

def main():
    start_url = input("Enter the starting URL of the portal: ")
    try:
        max_depth = int(input("Enter the maximum crawl depth (default: 5): ") or 5)
    except ValueError:
        max_depth = 5
        print("Invalid depth, using default depth of 5.")

    try:
        request_timeout = int(input("Enter the request timeout in seconds (default: 3): ") or 3)
    except ValueError:
        request_timeout = 3
        print("Invalid timeout, using default timeout of 3 seconds.")

    try:
        delay = float(input("Enter the delay between requests in seconds (default: 0.1): ") or 0.1)
    except ValueError:
        delay = 0.1
        print("Invalid delay, using default delay of 0.1 seconds.")

    scraper = WebScraper(start_url, max_depth, request_timeout, delay)
    scraper.crawl()

    search_engine = SearchEngine(scraper.scraped_data)

    while True:
        search_query = input("\nEnter your search query (or type 'exit' to quit): ")
        if search_query.lower() == 'exit':
            break

        case_sensitive_input = input("Perform case-sensitive search? (yes/no, default: no): ").lower()
        case_sensitive = case_sensitive_input == 'yes'

        results = search_engine.search(search_query, case_sensitive)

        if results:
            print("\nSearch Results:")
            for url, snippet in results.items():
                print(f"- URL: {url}")
                print(f"  Snippet: {snippet}")
        else:
            print("No results found for your query.")

if __name__ == "__main__":
    main()
