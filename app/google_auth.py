import os
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, auth
import secrets

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth = OAuth()

# Configure Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'redirect_uri': os.getenv("GOOGLE_REDIRECT_URI")
    }
)

@router.get("/google/login")
async def google_login(request: Request):
    """Redirect user to Google login page"""
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google's callback after user authentication"""
    try:
        # Get token and user info from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Authentication failed")
        
        email = user_info.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists
        db_user = db.query(models.User).filter(models.User.email == email).first()
        
        if not db_user:
            # Create new user
            username = user_info.get('name', email.split('@')[0])
            # Generate random password for OAuth users (they won't use password login)
            random_password = secrets.token_urlsafe(32)
            hashed_password = auth.get_password_hash(random_password)
            
            db_user = models.User(
                email=email,
                username=username,
                hashed_password=hashed_password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            print(f"Created new user via Google: {email}")
        
        # Create JWT token for the user
        access_token = auth.create_access_token(data={"sub": db_user.email})
        
        # Redirect to frontend with token
        # The frontend will catch this token and store it
        frontend_url = f"http://localhost:5173/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        print(f"Google auth error: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")