# Feature Websearch
# Complex Web Scraper and Search Engine

This Python script provides a comprehensive solution for scraping all accessible pages within a given website portal and then searching through the collected content. It utilizes the `requests` library for fetching web pages and `BeautifulSoup` for parsing HTML.

## Features

* **Recursive Crawling:** Explores all links within the specified portal up to a defined maximum depth.
* **Domain Restriction:** Ensures that the crawler stays within the domain of the initial URL.
* **Text Extraction:** Extracts the main textual content from each page, removing HTML tags, script, and style elements.
* **Respectful Crawling:** Includes a configurable delay between requests to avoid overloading the website's server.
* **Configurable Parameters:** Allows users to set the starting URL, maximum crawl depth, request timeout, and delay.
* **Simple Search Engine:** Enables users to search for specific queries within the scraped content.
* **Case-Sensitive/Insensitive Search:** Supports both case-sensitive and case-insensitive searches.
* **Search Results with Snippets:** Displays the URL of the matching page along with a snippet of the content where the query was found.
* **User-Agent Header:** Includes a default user-agent, which can be customized.

## How to Run

1.  **Prerequisites:**
    * Python 3.x installed on your system.
    * Install the required libraries:
        ```bash
        pip install requests beautifulsoup4
        ```

2.  **Save the Script:**
    * Save the provided Python code as a file (e.g., `web_search.py`).

3.  **Run from the Command Line:**
    * Open your terminal or command prompt.
    * Navigate to the directory where you saved the file.
    * Execute the script using:
        ```bash
        python web_search.py
        ```

4.  **Enter Input:**
    * The script will prompt you to enter the following information:
        * **Starting URL of the portal:** The main URL of the website you want to scrape.
        * **Maximum crawl depth (default: 5):** How many levels deep the crawler should go. A depth of 1 will only scrape the initial page and the pages directly linked from it.
        * **Request timeout in seconds (default: 3):** How long to wait for a response from the server before timing out.
        * **Delay between requests in seconds (default: 0.1):** The time the script will wait between fetching each page.

5.  **Crawling Process:**
    * The script will start crawling from the specified URL, displaying the URLs it is currently processing and the depth.
    * Once the crawling is finished (or the maximum depth is reached), it will indicate the number of pages found.

6.  **Search Queries:**
    * You will then be prompted to enter your search query.
    * Type your search term and press Enter.
    * You will be asked if you want to perform a case-sensitive search (enter 'yes' for case-sensitive, 'no' or press Enter for case-insensitive).
    * The script will display any matching URLs and a snippet of the content where the query was found.
    * You can continue entering search queries until you type 'exit'.

## Configuration

The script takes the following configuration parameters as input during runtime:

* **Starting URL:** The entry point for the web scraping process.
* **Maximum Crawl Depth:** Controls how far the scraper will navigate from the starting URL. A higher depth will explore more pages but will take longer
