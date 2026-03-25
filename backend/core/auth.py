import os
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Service role key

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: Supabase credentials missing from .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

def get_current_user(auth: HTTPAuthorizationCredentials = Security(security)):
    token = auth.credentials
    try:
        # Verify the token with Supabase
        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user = response.user
        return User(
            id=user.id,
            email=user.email,
            name=user.user_metadata.get("full_name") or user.user_metadata.get("name"),
            picture=user.user_metadata.get("avatar_url") or user.user_metadata.get("picture")
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

# Legacy helper removed: authenticate_user (Supabase handles this on frontend)
# Legacy helper removed: verify_google_token (Supabase handles this via OAuth providers)
