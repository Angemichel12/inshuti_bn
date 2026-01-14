from fastapi import FastAPI
from app.database import engine, Base
from app.users import routes

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="User Registration API",
    description="A simple user registration system",
    version="1.0.0"
)

# Include user routes
app.include_router(routes.router)

@app.get("/")
def read_root():
    """
    Root endpoint - just to test if API is working
    """
    return {
        "message": "Welcome to User Registration API",
        "docs": "/docs"
    }