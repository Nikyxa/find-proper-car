import os
import sqlite3
from time import sleep

import telebot
from dotenv import load_dotenv

load_dotenv()

bot_token = os.environ["BOT_TOKEN"]

channel_id = os.environ["CHANNEL_ID"]

bot = telebot.TeleBot(bot_token)

conn = sqlite3.connect("car_data.db")
cursor = conn.cursor()


def send_photo_to_channel(photo_url, caption):
    bot.send_photo(chat_id=channel_id, photo=photo_url, caption=caption)


def retrieve_cars_data():
    select_query = "SELECT id, photo_ria, model, price, mileage, ria_url, auction_url, is_sent, is_sold FROM cars"
    cursor.execute(select_query)
    cars_data = cursor.fetchall()

    return cars_data


def retrieve_price_value(car_price):
    if car_price:
        price_list = car_price.split()
        price = ""
        price += "".join(num for num in price_list if num.isnumeric())
        return int(price)


def is_sold_message(car_id, sold):
    if sold:
        message = f"The Car {car_id} has already been sold."
        bot.send_message(channel_id, message, parse_mode="Markdown")


def update_price_message(name_car, new_price, last_price):
    price_change = (
        "decreased"
        if retrieve_price_value(new_price) < retrieve_price_value(last_price)
        else "increased"
    )
    message = f"The price of Car {name_car} has {price_change}.\nPrevious price: {last_price}\nUpdated price: {new_price}"
    bot.send_message(channel_id, message, parse_mode="Markdown")


def send_message_to_channel():
    cars_data = retrieve_cars_data()
    for car in cars_data:
        (
            id,
            photo_ria,
            model,
            price,
            mileage,
            ria_url,
            auction_url,
            is_sent,
            is_sold,
        ) = car
        if not is_sent:
            message_text = f"{model}\n 💵 {price} \n ⚙ {mileage} тис. км\n 🔗 [autoria]({ria_url})\n 🇺🇸 [bidfax]({auction_url})"

            bot.send_message(channel_id, message_text, parse_mode="Markdown")
            update_query = "UPDATE cars SET is_sent = 1 WHERE id = ?"
            cursor.execute(update_query, (id,))
            conn.commit()

            sleep(3)

            is_sold_message(ria_url, is_sold)
