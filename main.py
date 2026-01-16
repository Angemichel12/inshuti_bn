from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.users import routes
from app.users.services import initialize_default_roles

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize default roles
db = SessionLocal()
try:
    initialize_default_roles(db)
finally:
    db.close()

# Create FastAPI application
app = FastAPI(
    title="User Registration API",
    description="A simple user registration system with role management",
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