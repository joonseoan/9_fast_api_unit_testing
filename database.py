from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
    PostgreSQL
"""
SQLALCHEMY_DATABASE_URL = "postgresql://root:qwer123@localhost/todosapp"

# same as postgresql, and mysql
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# same as sqlite, postgresql, and mysql
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
