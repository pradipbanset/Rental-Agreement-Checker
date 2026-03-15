# from fastapi import APIRouter, Request, HTTPException, Depends
# from fastapi.responses import RedirectResponse
# from authlib.integrations.starlette_client import OAuth
# from app.core.config import settings
# from app.core.database import get_db
# from app.models.db_models import User
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# import jwt as pyjwt  # Explicit alias to avoid conflicts
# from datetime import datetime, timedelta

# router = APIRouter()

# # Add Pydantic model for JSON request
# class EmailLoginRequest(BaseModel):
#     email: str
#     name: str = None

# # OAuth setup
# oauth = OAuth()
# CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
# oauth.register(
#     name='google',
#     client_id=settings.GOOGLE_CLIENT_ID,
#     client_secret=settings.GOOGLE_CLIENT_SECRET,
#     server_metadata_url=CONF_URL,
#     client_kwargs={'scope': 'openid email profile'}
# )

# # Email login endpoint
# @router.post("/login")
# def login_email(
#     request: EmailLoginRequest,
#     db: Session = Depends(get_db)
# ):
#     if not request.email:
#         raise HTTPException(status_code=400, detail="Email required")
    
#     # Check if user exists; if not, create new
#     user = db.query(User).filter(User.email == request.email).first()
    
#     if not user:
#         # Create new user with provided name or extract from email
#         display_name = request.name if request.name else request.email.split("@")[0]
#         user = User(
#             email=request.email, 
#             name=display_name,
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#         print(f"✓ New user created: {request.email} (ID: {user.id})")
#     else:
#         print(f"✓ Existing user logged in: {request.email} (ID: {user.id})")
    
#     # Create JWT token using PyJWT
#     token = pyjwt.encode(
#         {
#             "user_id": user.id, 
#             "email": user.email, 
#             "exp": datetime.utcnow() + timedelta(days=7)
#         },
#         settings.SECRET_KEY,
#         algorithm="HS256"
#     )
    
#     return {
#         "id": user.id,
#         "email": user.email,
#         "name": user.name,
#         "token": token
#     }

# # Google login redirect
# @router.get("/login/google")
# async def login_google(request: Request):
#     redirect_uri = settings.GOOGLE_REDIRECT_URI
#     return await oauth.google.authorize_redirect(request, redirect_uri)

# # Google OAuth callback
# @router.get("/login/google/callback")
# async def google_callback(request: Request, db: Session = Depends(get_db)):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#         user_info = await oauth.google.parse_id_token(request, token)
        
#         # Create or fetch user
#         user = db.query(User).filter(User.email == user_info['email']).first()
        
#         if not user:
#             user = User(
#                 email=user_info['email'], 
#                 name=user_info.get('name', user_info['email'].split('@')[0]),
#             )
#             db.add(user)
#             db.commit()
#             db.refresh(user)
#             print(f"✓ New Google user created: {user_info['email']} (ID: {user.id})")
        
#         # JWT token using PyJWT
#         jwt_token = pyjwt.encode(
#             {
#                 "user_id": user.id, 
#                 "email": user.email, 
#                 "exp": datetime.utcnow() + timedelta(days=7)
#             },
#             settings.SECRET_KEY,
#             algorithm="HS256"
#         )
        
#         # Redirect to frontend chat page with token
#         frontend_redirect = f"http://localhost:3000/chat?token={jwt_token}&email={user.email}&id={user.id}"
#         return RedirectResponse(frontend_redirect)
        
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))








from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from app.core.config import settings
from app.core.database import get_db
from app.models.db_models import User
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt as pyjwt  # Explicit alias to avoid conflicts
from datetime import datetime, timedelta

router = APIRouter()

# Add Pydantic model for JSON request
class EmailLoginRequest(BaseModel):
    email: str
    name: str = None

# OAuth setup
oauth = OAuth()
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url=CONF_URL,
    client_kwargs={'scope': 'openid email profile'}
)

# Email login endpoint
@router.post("/login")
def login_email(
    request: EmailLoginRequest,
    db: Session = Depends(get_db)
):
    if not request.email:
        raise HTTPException(status_code=400, detail="Email required")
    
    # Check if user exists; if not, create new
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Create new user with provided name or extract from email
        display_name = request.name if request.name else request.email.split("@")[0]
        user = User(
            email=request.email, 
            name=display_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ New user created: {request.email} (ID: {user.id})")
    else:
        print(f"✓ Existing user logged in: {request.email} (ID: {user.id})")
    
    # Create JWT token using PyJWT
    token = pyjwt.encode(
        {
            "user_id": user.id, 
            "email": user.email, 
            "exp": datetime.utcnow() + timedelta(days=7)
        },
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "token": token
    }

# Google login redirect - KEEP THIS!
@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    print(f"🔍 DEBUG - Settings loaded:")
    print(f"   CLIENT_ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
    print(f"   REDIRECT_URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)



@router.get("/login/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        print("🔍 Processing Google callback...")
        
        # Get the access token
        token = await oauth.google.authorize_access_token(request)
        
        print(f"✅ Token received: {token.keys()}")
        
        # Get user info from the userinfo endpoint instead of parsing id_token
        user_info = token.get('userinfo')
        
        # If userinfo is not in token, fetch it
        if not user_info:
            resp = await oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo', token=token)
            user_info = resp.json()
        
        print(f"👤 User info: {user_info.get('email')}")
        
        # Create or fetch user
        user = db.query(User).filter(User.email == user_info['email']).first()
        
        if not user:
            user = User(
                email=user_info['email'], 
                name=user_info.get('name', user_info['email'].split('@')[0]),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✓ New Google user created: {user_info['email']} (ID: {user.id})")
        else:
            print(f"✓ Existing Google user logged in: {user_info['email']} (ID: {user.id})")
        
        # JWT token using PyJWT
        jwt_token = pyjwt.encode(
            {
                "user_id": user.id, 
                "email": user.email, 
                "exp": datetime.utcnow() + timedelta(days=7)
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        print(f"✅ JWT created, redirecting to frontend...")
        
        # Redirect to OAuth callback page (NOT directly to /chat)
        frontend_redirect = f"http://localhost:3000/auth/callback?token={jwt_token}&email={user.email}&id={user.id}"
        return RedirectResponse(frontend_redirect)
        
    except Exception as e:
        print(f"❌ OAuth error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))