import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to the database using the same credentials as in app.py
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

conn = get_db_connection()
cursor = conn.cursor()

# Number of users for the benchmark test
iterations = 100 

print(f"Starting benchmark: generating {iterations} records...")

start_time = time.time()

for i in range(iterations):
    # We are not inserting data (INSERT), we are just testing 
    # the execution speed of the function within the database
    cursor.execute("SELECT * FROM generate_user(%s, %s)", (i, 'de'))
    cursor.fetchone()

end_time = time.time()
total_time = end_time - start_time
users_per_second = iterations / total_time

print(f"Result: {users_per_second:.2f} users/sec")

cursor.close()
conn.close()