import psycopg2

def connect_db():
    conn = psycopg2.connect(
        database="ptt_db", 
        user="ronyeh", 
        host="127.0.0.1", 
        port="5432"
    )
    return conn

# conn = psycopg2.connect(database="ptt_db", user="ronyeh", host="127.0.0.1", port="5432")
# print("Opened database successfully")
