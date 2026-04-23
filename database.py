import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(database=os.getenv("DB_DATABASE"),
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"))

cursor = conn.cursor()

create_table_query = '''CREATE TABLE IF NOT EXISTS lookup_data(
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(20) NOT NULL,
    locale VARCHAR(10) NOT NULL,
    val VARCHAR(100) NOT NULL
);'''
create_index_query = '''CREATE INDEX idx_category_locale ON lookup_data(category_name,locale);'''
#Executing a SQL query
cursor.execute(create_table_query)

cursor.execute('''INSERT INTO lookup_data(category_name, locale, val)
VALUES ('first_name','en','John'),
('first_name', 'en', 'Alice'),
('last_name', 'en', 'Smith'),
('last_name', 'en', 'Doe'),
('city', 'en', 'New York'),
('city', 'en', 'London');''')

cursor.execute('''INSERT INTO lookup_data(category_name, locale, val)
VALUES('first_name','de','Hans'),
('first_name', 'de', 'Greta'),
('last_name', 'de', 'Müller'),
('last_name', 'de', 'Schmidt'),
('city', 'de', 'Berlin'),
('city', 'de', 'Munich');''')

# cursor.execute('''SELECT * FROM lookup_data WHERE category_name = 'first_name' AND locale = 'de';''')
conn.commit()
