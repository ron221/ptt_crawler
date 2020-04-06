from conn_info import connect_db

def create1():
    cur.execute('''CREATE TABLE article(
        article_id SERIAL PRIMARY KEY,
        title CHAR(150),
        author_id CHAR(100),
        author_name CHAR(100),
        time TIMESTAMP,
        content TEXT,
        url TEXT UNIQUE)'''
    )

    conn.commit()

def create2():
    cur.execute('''CREATE TABLE push(
        push_id SERIAL PRIMARY KEY,
        article_id INT REFERENCES article(article_id) ON DELETE CASCADE,
        push_author CHAR(100),
        push_content TEXT,
        push_time TIMESTAMP)'''
    )
    conn.commit()

if __name__ == '__main__':
    conn = connect_db()
    cur = conn.cursor()
    create1()
    create2()
    conn.close()