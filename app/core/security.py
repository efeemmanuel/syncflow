from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
import secrets
from app.core.redis import redis_client


# sets up bcrypt hasher
password_hash = PasswordHash.recommended()


# prevents timing attacks
DUMMY_HASH = password_hash.hash("dummypassword")



# verify password coming in
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# hash password
def get_password_hash(password):
    return password_hash.hash(password)



# extract token from header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



# create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, settings.algorithm)
    return encoded_jwt



# verify the jwt token
def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # decode the token with secret key
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        # get user id
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return user_id
    except InvalidTokenError:
        raise credentials_exception   







'''
for invitation tokens 
    '''

# generates a cryptographically secure random token.
def create_invite_token() -> str:
    # generates a secure random token
    return secrets.token_urlsafe(32)


# saves token to Redis with email, company_id and role attached
async def save_invite_token(email: str, company_id: int, role: str):
    token = create_invite_token()
    # store in redis, expires in 48 hours
    await redis_client.setex(
        f"invite:{token}",
        172800,  # 48 hours in seconds
        f"{email}:{company_id}:{role}"
    )
    return token


# looks up token in Redis, returns the data
async def verify_invite_token(token: str):
    data = await redis_client.get(f"invite:{token}")
    if not data:
        raise ValueError("Invalid or expired invite token")
    email, company_id, role = data.split(":")
    return {"email": email, "company_id": int(company_id), "role": role}




