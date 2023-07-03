from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URl = "https://auto.ria.com/uk/"
CARS_URL = urljoin(BASE_URl, "search/?categories.main.id=1&brand.id[0]=79&model.id[0]=2104&indexName=auto,order_auto,newauto_search&damage.not=0&country.import.usa.not=0&size=10")


def parse_auto_ria():
    response = requests.get(CARS_URL).content
    soup = BeautifulSoup(response, 'html.parser')
    print(soup.prettify())

    car_names = soup.find_all('div', class_='content')
    for name in car_names:
        title_and_year = name.find('a', class_='address').text.strip()
        print(title_and_year)

    car_prices = soup.find_all('div', class_='price-ticket')
    for car_price in car_prices:
        price = car_price.find('span', class_='bold size22 green').text.strip()
        print(price + "$")

    car_values = soup.find_all('div', class_='definition-data')
    for car_value in car_values:
        mileage = car_value.find('li', class_='item-char js-race').text.strip()
        location = car_value.find('li', class_='item-char view-location js-location').text.split()
        print(mileage, location[0])

    car_urls = soup.find_all('div', class_='content-bar')
    for car_url in car_urls:
        url = car_url.find('a', class_='m-link-ticket')["href"]
        image = car_url.find('img', class_='outline m-auto')["src"]
        print(url, image)

        # # Обробка фотографій автомобіля
        # photos = listing.find_all('img')
        # photo_links = [photo['src'] for photo in photos]
parse_auto_ria()