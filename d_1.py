from fastapi import HTTPException, Header
import jwt , os
from d_2 import user_collection

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
expiration_time = os.getenv("JWT_EXPIRATION_MINUTES") or 0
JWT_EXPIRATION_MINUTES = int(expiration_time)

async def check_user_is_admin(authorization: str = Header(...)):
    email = await get_email_from_token(authorization)
    user = user_collection.find_one({'email': email})
    if user is None:
        raise HTTPException(detail='User not found', status_code=404)
    if user['user_type'] != 'admin':
        raise HTTPException(detail='User is not Admin', status_code=400)
    return user

async def get_email_from_token(authorization: str = Header(...)):
    try:
        decode_token = decode_jwt_token(authorization)
        email = decode_token["sub"]
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(detail="Invalid token", status_code=400)
    return email

def decode_jwt_token(token: str):
    try:
        token = token.split()[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        print(e)
        return {}
    
async def get_status_list_from_query(statuses):
    status_list = statuses.split(",")
    lst = []
    for status in status_list:
        lst.append(status.strip())
    return lst