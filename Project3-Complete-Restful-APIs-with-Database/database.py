from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"  # location of the database in the file system (current pwd)
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# check_same_thread=False for SQLite

# PostgreSQL
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:ppk249609@localhost/TodoApp"
# servername://username:password@localhost/dbname)
# engine = create_engine(SQLALCHEMY_DATABASE_URL)


# MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:ppk249609@localhost:3306/TodoApp"
# servername://username:password@localhost:port/dbname)
engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
