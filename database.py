import sqlite3

conn = sqlite3.connect('car_data.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS cars
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              model TEXT,
              price INTEGER,
              url TEXT,
              photo TEXT,
              mileage TEXT,
              location TEXT,
              unique_id TEXT,
              is_sold INTEGER DEFAULT 0)''')

c.execute('''CREATE TABLE IF NOT EXISTS price_history
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              car_id INTEGER,
              price INTEGER,
              sold INTEGER,
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (car_id) REFERENCES cars (id))''')

conn.commit()

conn.close()
