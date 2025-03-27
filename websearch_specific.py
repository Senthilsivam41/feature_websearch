import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_portal(url, search_text=None):
    """
    Scrapes data (links, images, content from Div areas) from a given portal URL.

    Args:
        url (str): The URL of the portal to scrape.
        search_text (str, optional): If provided, the function will try to focus
                                      on content within Div areas related to this text.
                                      Defaults to None.

    Returns:
        dict: A dictionary containing the scraped data:
              {
                  'links': list of str,
                  'images': list of str,
                  'content': list of str
              }
              Returns None if the request fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        scraped_data = {
            'links': [],
            'images': [],
            'content': []
        }

        # Extract all links
        for link_tag in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link_tag['href'])
            scraped_data['links'].append(absolute_url)

        # Extract all image URLs
        for img_tag in soup.find_all('img'):
            if 'src' in img_tag.attrs:
                absolute_url = urljoin(url, img_tag['src'])
                scraped_data['images'].append(absolute_url)

        # Extract content from Div areas related to search text
        if search_text:
            relevant_div_content = set()
            for element in soup.find_all(string=lambda text: text and search_text.lower() in text.lower()):
                parent = element.find_parent()
                while parent:
                    if parent.name == 'div':
                        div_text = parent.get_text(separator='\n', strip=True)
                        relevant_div_content.add(div_text)
                        break  # Found the nearest div, no need to go further up for this element
                    parent = parent.parent
            scraped_data['content'] = list(relevant_div_content)
        else:
            # If no search text, extract content from all Div areas
            all_div_content = set()
            for div_tag in soup.find_all('div'):
                div_text = div_tag.get_text(separator='\n', strip=True)
                if div_text:  # Avoid adding empty div content
                    all_div_content.add(div_text)
            scraped_data['content'] = list(all_div_content)

        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None

if __name__ == "__main__":
    portal_url = input("Enter the URL of the portal to scrape: ")
    search_query = input("Enter the text to search for (leave blank to scrape all Div content): ")

    scraped_info = scrape_portal(portal_url, search_query if search_query else None)

    if scraped_info:
        print("\n--- Scraped Data ---")
        print("\nLinks:")
        for link in scraped_info['links']:
            print(f"- {link}")

        print("\nImages:")
        for image in scraped_info['images']:
            print(f"- {image}")

        print("\nContent from Div areas:")
        for content_part in scraped_info['content']:
            print(f"{content_part}\n---")
    else:
        print("Failed to scrape the portal.")
