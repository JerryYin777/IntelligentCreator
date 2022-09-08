from sqlalchemy import create_engine

engine = create_engine("mysql://root:1234@127.0.0.1:3306/news")

