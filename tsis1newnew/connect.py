import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="phonebook",
        user="postgres",
        password="1234"
    )