from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



# URL_DATABASE = 'postgresql://cactus:99936022MCmc@localhost:5432/fastapi_with_pg'

# ssl_context = ssl.create_default_context()
# ssl_context.check_hostname = False
# ssl_context.verify_mode = ssl.CERT_NONE
# engine = sa.create_engine(
#     "postgresql+pg8000://scott:tiger@192.168.0.199/test",
#     connect_args={"ssl_context": ssl_context},
# )

URL_DATABASE = 'postgresql+psycopg2://cactus:rH1jdjGcVGEuKQ7wSFg20dqEjn7fXcGI@dpg-cnq6s0v79t8c7396mmo0-a.frankfurt-postgres.render.com/task2?sslmode=require'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()