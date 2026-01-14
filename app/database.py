from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
# This is like opening a connection to your database
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
# This will be used to create database sessions (like opening a conversation with the database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our models
# All our database tables will inherit from this
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    This function creates a new database session for each request
    and closes it when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()