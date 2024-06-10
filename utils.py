import requests
from bs4 import BeautifulSoup

def scrape_image(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_element = soup.find('img')
        if image_element:
            return image_element['src']
        else:
            return None
    except Exception as e:
        print(f"Error scraping image: {e}")
        return None
