import psycopg2

def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="phonebook_db",
        user="postgres",
        password="1234",
        port=5432
    )
    return conn