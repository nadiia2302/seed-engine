from flask import Flask, render_template, request
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        database=os.getenv("DB_DATABASE"),
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

@app.route('/')
def index():
    seed = request.args.get('seed', 1, type=int)
    locale = request.args.get('locale', 'de')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
  
    insert_sql = '''
    INSERT INTO users (first_name, last_name, city, lat, lon, height, weight, seed, locale)
    SELECT *, %s, %s FROM generate_user(%s, %s);
    '''
    cur.execute(insert_sql, (seed, locale, seed, locale))
    conn.commit()
    
    
    cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
    user = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', user=user, seed=seed, locale=locale)

if __name__ == '__main__':
    print("Running Flask...")
    app.run(debug=True)