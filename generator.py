import random
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
def get_data_count(cursor,category,locale):
    get_data_query = "SELECT COUNT(*) FROM lookup_data WHERE category_name = %s and locale = %s"
    cursor.execute(get_data_query,(category,locale))
    result = cursor.fetchone()
    return result[0]
def get_random_value(cursor,category, locale, seed):
    count = get_data_count(cursor,category, locale)
    random.seed(seed)
    get_random_index = random.randint(0,count-1)
    query_value = "SELECT val FROM lookup_data WHERE category_name = %s and locale = %s LIMIT 1 OFFSET %s"
    cursor.execute(query_value,(category,locale, get_random_index))
    result = cursor.fetchone()
    return result[0]
conn = psycopg2.connect(database=os.getenv("DB_DATABASE"),
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"))

cursor = conn.cursor()

def generate_user(cursor, user_id, locale):
    generate_user_data = {}
    generate_user_data['user_id'] = user_id
    generate_user_data['first_name'] = get_random_value(cursor,'first_name',locale,user_id)
    generate_user_data['last_name'] = get_random_value(cursor, 'last_name',locale, user_id)
    generate_user_data['city'] = get_random_value(cursor, 'city', locale, user_id )

    return generate_user_data

users_table = '''CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    city VARCHAR(20))'''
cursor.execute(users_table)
conn.commit()

print("Generated table of users:")
for i in range (1,11):
    users = generate_user(cursor, i, 'de')
    print(users)

    fill_user_table = '''INSERT INTO users (id, first_name, last_name, city)
    VALUES (%s, %s,%s, %s) '''
    cursor.execute(fill_user_table,(users['user_id'], users['first_name'], users['last_name'], users['city']))
    conn.commit()