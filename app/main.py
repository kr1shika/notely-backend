from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import users, notes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notely API", version="1.0.0")

# CORS middleware - MUST be the first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://notely-ruby.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(users.router)
app.include_router(notes.router)

@app.get("/")
def root():
    return {"message": "Welcome to Notely API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}