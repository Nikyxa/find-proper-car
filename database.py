import sqlite3

conn = sqlite3.connect("car_data.db")
c = conn.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS cars
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              model TEXT,
              price INTEGER DEFAULT 0,
              mileage TEXT,
              ria_url TEXT,
              page_id TEXT,
              photo_ria TEXT,
              auction_url TEXT,
              is_sold INTEGER DEFAULT 0,
              is_sent INTEGER DEFAULT 0)"""
)

conn.commit()

conn.close()
