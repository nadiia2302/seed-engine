import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    database=os.getenv("DB_DATABASE"),
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS users;")


cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    city TEXT,
    lat NUMERIC,
    lon NUMERIC,
    height NUMERIC,
    weight NUMERIC,
    seed INT,
    locale TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')


cursor.execute('''
CREATE OR REPLACE FUNCTION get_random_value(p_seed INT, p_locale TEXT, p_category TEXT)
RETURNS TEXT AS $$
DECLARE 
    v_count INT; v_offset INT; v_result TEXT;
BEGIN 
    SELECT COUNT(*) INTO v_count FROM lookup_data WHERE category_name = p_category AND locale = p_locale;
    IF v_count = 0 THEN RETURN 'Data missing'; END IF;
    v_offset := abs(('x' || substr(md5(concat(p_category, p_seed)),1,8))::bit(32)::int) % v_count;
    SELECT val INTO v_result FROM lookup_data WHERE category_name = p_category AND locale = p_locale LIMIT 1 OFFSET v_offset;
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;''')

cursor.execute('''
CREATE OR REPLACE FUNCTION get_random_lat(p_seed INT) RETURNS NUMERIC AS $$
BEGIN
    RETURN asin(2 * (abs(('x' || substr(md5(concat('lat', p_seed)), 1, 8))::bit(32)::int) / 4294967295.0) - 1) * 180 / pi();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_random_lon(p_seed INT) RETURNS NUMERIC AS $$
BEGIN
    RETURN ((abs(('x' || substr(md5(concat('lon', p_seed)), 1, 8))::bit(32)::int) / 4294967295.0) * 360) - 180;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_random_normal(p_seed INT, p_mean NUMERIC, p_stddev NUMERIC) RETURNS NUMERIC AS $$
DECLARE
    u1 NUMERIC; u2 NUMERIC;
BEGIN
    u1 := abs(('x' || substr(md5(concat('n1', p_seed)), 1, 8))::bit(32)::int) / 4294967295.0;
    u2 := abs(('x' || substr(md5(concat('n2', p_seed)), 1, 8))::bit(32)::int) / 4294967295.0;
    RETURN (sqrt(-2 * ln(u1 + 0.000001)) * cos(2 * pi() * u2) * p_stddev) + p_mean;
END;
$$ LANGUAGE plpgsql;''')


cursor.execute("DROP FUNCTION IF EXISTS generate_user(INT, TEXT);")
cursor.execute('''
CREATE OR REPLACE FUNCTION generate_user(p_seed INT, p_locale TEXT)
RETURNS TABLE(first_name TEXT, last_name TEXT, city TEXT, lat NUMERIC, lon NUMERIC, height NUMERIC, weight NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        get_random_value(p_seed, p_locale, 'first_name'),
        get_random_value(p_seed, p_locale, 'last_name'),
        get_random_value(p_seed, p_locale, 'city'),
        get_random_lat(p_seed),
        get_random_lon(p_seed),
        round(get_random_normal(p_seed, 175, 7), 1),
        round(get_random_normal(p_seed + 1, 70, 10), 1);
END;
$$ LANGUAGE plpgsql;''')

conn.commit()


seed = 101
locale = 'de'


sql_insert = '''
INSERT INTO users (first_name, last_name, city, lat, lon, height, weight, seed, locale)
SELECT first_name, last_name, city, lat, lon, height, weight, %s, %s 
FROM generate_user(%s, %s);
'''

cursor.execute(sql_insert, (seed, locale, seed, locale))
conn.commit()


cursor.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 1;")
result = cursor.fetchone()
print(f"The last user added to the database (with settings): {result}")