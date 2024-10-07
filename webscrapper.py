import requests
from bs4 import BeautifulSoup
import re
from requests.exceptions import RequestException
import time

# Use requests.Session() to maintain a persistent connection
session = requests.Session()

# Function to handle searching and getting the first relevant link
def get_info(search_term):
    search_url = "https://www.gov.uk/search/all?keywords=" + search_term.replace(' ', '+') + "&order=relevance"
    try:
        response = session.get(search_url)
        response.raise_for_status()  # Raise error for bad HTTP status
    except RequestException as e:
        return f"Failed to retrieve search results: {str(e)}"

    soup = BeautifulSoup(response.content, 'html.parser')
    result = soup.find('ul', class_='gem-c-document-list govuk-!-margin-bottom-5')

    if result:
        first_link = result.find('a')['href']
        full_link = "https://www.gov.uk" + first_link
        return Main_info(full_link)
    else:
        return "No search results found."

# Function to retrieve the main information from the found link
def Main_info(full_link):
    next_content = {}
    pdf_file = False

    try:
        # Fetch page content using the session
        page_response = session.get(full_link)
        page_response.raise_for_status()
    except RequestException as e:
        return f"Failed to load the page: {full_link}. Error: {str(e)}"

    page_soup = BeautifulSoup(page_response.content, 'html.parser')

    # Extract the relevant page section
    page_result = page_soup.find('div', class_='direction-ltr govuk-width-container')
    if not page_result:
        return "No relevant content found on the page."

    # Find the main heading
    heading = page_result.find('h1', class_='gem-c-title__text govuk-heading-xl') or page_result.find('h1', class_='gem-c-title__text govuk-heading-l')

    # Check if there's PDF content or regular HTML content
    if page_result.find('span', class_='govuk-caption-xl gem-c-title__context'):
        info_result = page_result.find('div', class_='govuk-grid-row gem-print-columns-none') or None

        # Handle the case for PDFs
        if not info_result:
            final_link = page_result.find('a', class_='govuk-link gem-c-attachment__link')['href']
            if "application/pdf" in page_response.headers.get('Content-Type', ''):
                pdf_file = True
                return heading.get_text() + " Link to the PDF file: " + final_link

            # If HTML, load the new page
            new_response = session.get("https://www.gov.uk" + final_link)
            final_soup = BeautifulSoup(new_response.content, 'html.parser')
            info_result = final_soup.find('div', class_='govuk-grid-column-three-quarters-from-desktop contents-container')
    else:
        info_result = page_result.find('div', class_='govuk-grid-column-two-thirds govuk-!-margin-top-6')
        content_result = page_result.find('ol', class_='gem-c-contents-list__list')

        # Remove first list item (if needed) and collect links
        if content_result:
            first_li = content_result.find('li')
            if first_li:
                first_li.decompose()  # Remove first <li> element
            links = content_result.find_all('a', class_='gem-c-contents-list__link govuk-link')
            for link in links:
                link_text = link.get_text(strip=True)
                href = link['href']
                next_content[link_text] = full_link + href

    # Clean up unnecessary navigation/pagination elements
    if info_result and not pdf_file:
        nav_to_remove = info_result.find('nav', class_='govuk-pagination govuk-pagination--block')
        div_to_remove = info_result.find('div', class_='responsive-bottom-margin')
        if nav_to_remove:
            nav_to_remove.decompose()
        if div_to_remove:
            div_to_remove.decompose()

        # Extract and clean up the text content
        text_content = heading.get_text() + re.sub(r'\n+', '\n', info_result.get_text())
        return text_content, next_content
    else:
        return "No relevant content found."
