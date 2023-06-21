""" Scraping plants synchronously.
    Simple script to iterate pages and fetch the title from each page.
    To be used as a benchmark comparison against async version.
"""

from typing import Optional, List, Dict
import httpx
from bs4 import BeautifulSoup
from logging_config import configure_logger
from settings import BASE_URL, PAGE_LIMIT, PLANT_TYPE

logger = configure_logger(__name__)


def get_soup(url: str) -> BeautifulSoup:
    """
    Fetch URL content and parse it with BeautifulSoup.

    Parameters:
    url (str): The URL to fetch and parse.

    Returns:
    BeautifulSoup: Parsed HTML content.
    """
    response = httpx.get(url)
    logger.debug(f"Fetching and parsing URL: {url}")
    return BeautifulSoup(response.content, 'html.parser')


def get_by_class(soup: BeautifulSoup, tag: str, class_name: str) -> Optional[str]:
    """
    Find a tag with a specific class in the soup object and return its text.

    Parameters:
    soup (BeautifulSoup): BeautifulSoup object to search in.
    tag (str): HTML tag to find.
    class_name (str): Class of the HTML tag to find.

    Returns:
    str: Text of the found tag.
    """
    try:
        return soup.find(tag, {'class': class_name}).text.strip()
    except AttributeError:
        return None


def get_plant_details(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Collect details of one plant.

    Parameters:
    soup (BeautifulSoup): BeautifulSoup object to search in.

    Returns:
    Dict[str, str]: Dictionary with plant details.
    """
    data = {}
    data['title'] = get_by_class(soup, 'h1', 'h2 product-single__title')
    return data


def get_plant_links(soup: BeautifulSoup) -> Optional[List[str]]:
    """
    Find plant links in the soup object.

    Parameters:
    soup (BeautifulSoup): BeautifulSoup object to search in.

    Returns:
    List[str]: List of plant links.
    """
    try:
        return [f"{BASE_URL}{link.find('a')['href']}" for link in
                soup.findAll('div', {'class': 'grid-product__content'})]
    except AttributeError:
        logger.error("AttributeError when trying to find plant links in soup.", exc_info=True)
        return None


def main(main_url: str) -> None:
    """
    Main function to scrape plant details from main_url.

    Parameters:
    main_url (str): URL of the page with plants.

    Returns:
    None
    """

    logger.info(f"Starting scrape for {PLANT_TYPE.replace('-', ' ')} plants: {main_url}")
    for page in range(1, PAGE_LIMIT):

        logger.debug(f"Scraping page number {page}.")
        main_response = httpx.get(f'{main_url}?page={page}')
        main_soup = BeautifulSoup(main_response.content, 'html.parser')
        plant_links = get_plant_links(main_soup)

        if not plant_links:
            logger.info("No more plant links found. Stopping the script.")
            break

        plants = [get_plant_details(get_soup(link)) for link in plant_links]
        logger.info(f"Scraped {len(plants)} plant details for page {page}.")
        for plant in plants:
            print(plant['title'])


if __name__ == '__main__':
    search_url = f'{BASE_URL}/collections/{PLANT_TYPE}'
    main(search_url)
