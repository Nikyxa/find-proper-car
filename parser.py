import sqlite3
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from bot import update_price_message, send_message_to_channel

BASE_URl = "https://auto.ria.com/uk/"
CARS_URL = urljoin(BASE_URl, "search/?categories.main.id=1&brand.id[0]=79&model.id[0]=2104&indexName=auto,order_auto,newauto_search&damage.not=0&country.import.usa.not=0&size=100")


conn = sqlite3.connect("car_data.db")
cursor = conn.cursor()


def parse_cars_urls():
    response = requests.get(CARS_URL).content
    soup = BeautifulSoup(response, 'html.parser')

    cars = soup.find_all('div', class_='content-bar')
    car_urls = []
    for car in cars:
        url = car.find('a', class_='m-link-ticket')["href"]
        car_urls.append(url)
    return car_urls


def parse_one_page(url):
    page = requests.get(url).content
    page_soup = BeautifulSoup(page, 'html.parser')
    return page_soup


def insert_car_data(model, price, mileage, ria_url, page_id, photo_ria, auction_url, is_sold):
    conn = sqlite3.connect("car_data.db")
    cursor = conn.cursor()

    insert_query = '''
    INSERT INTO cars (model, price, mileage, ria_url, page_id, photo_ria, auction_url, is_sold)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    record_data = (model, price, mileage, ria_url, page_id, ",".join(photo_ria), auction_url, is_sold)
    cursor.execute(insert_query, record_data)

    conn.commit()
    conn.close()

def check_unique_cars(model, price, mileage, page_id, ria_url, auction_url):
    conn = sqlite3.connect("car_data.db")
    cursor = conn.cursor()

    select_query = "SELECT * FROM cars WHERE model = ? AND price = ? AND mileage = ? AND page_id = ? AND ria_url = ? AND auction_url = ?"
    cursor.execute(select_query, (model, price, mileage, page_id, ria_url, auction_url))
    existing_car = cursor.fetchone()

    return existing_car


def retrieve_last_price(page_id):
    select_query = "SELECT price FROM cars WHERE page_id = ?"
    cursor.execute(select_query, (page_id,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        return None


def parse_one_car():
    car_urls = parse_cars_urls()

    for car_url in car_urls:
        parse_url = parse_one_page(car_url)

        model = parse_url.find('h1', class_='head').text.strip()
        price = parse_url.find('div', class_='price_value').text.strip()
        mileage = parse_url.find('span', class_='size18').text.strip()
        ria_url = car_url

        page_url_parts = car_url.split("_")
        url_part = page_url_parts[3].split(".")
        page_id = url_part[0]

        photos = parse_url.find_all("img", class_="outline m-auto")
        photo_links = [photo['src'] for photo in photos]
        photo_ria = photo_links[:5]

        auction_script = parse_url.select_one("script[data-bidfax-pathname]")
        part_url = auction_script.get("data-bidfax-pathname")[7:]
        auction_url = f"https://bidfax.info{part_url}"

        is_sold = bool(parse_url.find("div", class_="gallery-order sold-out carousel"))

        if not check_unique_cars(model, price, mileage, page_id, ria_url, auction_url):
            last_price = retrieve_last_price(page_id)
            insert_car_data(model, price, mileage, ria_url, page_id, photo_ria, auction_url, is_sold)

            if last_price is None:
                continue
            if last_price != price:
                update_price_message(model, price, last_price)


def main_scraper():
    while True:
        parse_one_car()
        send_message_to_channel()
        time.sleep(10 * 60)


if __name__ == '__main__':
    main_scraper()
