from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import users, notes
from app.auth import google_auth 
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notely API", version="1.0.0")

# CORS middleware (allows React frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(notes.router)
app.include_router(google_auth.router)
@app.get("/")
def root():
    return {"message": "Welcome to Notely API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}