import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# engine.execute("DROP TABLE users CASCADE")
# engine.execute("DROP TABLE reviews CASCADE")
# engine.execute("DROP TABLE books CASCADE")

engine.execute(
 """CREATE TABLE books(
      id SERIAL PRIMARY KEY,
      isbn VARCHAR UNIQUE NOT NULL,
      title VARCHAR NOT NULL,
      author VARCHAR NOT NULL,
      year INTEGER NOT NULL
  )
 """
)

engine.execute(
  """CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username UNIQUE VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    password VARCHAR NOT NULL
   )
  """
)

engine.execute(
  """CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books,
    user_id INTEGER REFERENCES users,
    review VARCHAR NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5)
   )
  """
)

f = open('books.csv')
books = csv.reader(f)

for isbn, title, author, year in books:
    db.execute("INSERT INTO BOOKS(isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {
      "isbn": isbn,
      "title": title,
      "author": author,
      "year": year
    })
    print(f"Added {title} into books")
db.commit()
