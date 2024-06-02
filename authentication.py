# native library imports
import os
from typing import Dict

# 3rd party library imports
import jwt
from fastapi import HTTPException, Header

# local imports
from database_setup import user_collection


class Authentication:
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

    @staticmethod
    async def check_user_is_admin(authorization: str = Header(...)):
        """
        Checks if user is admin. Raises exception fs user is not admin.
        :param authorization: Authorization token
        :return:
        """
        email = await Authentication.get_email_from_token(authorization)
        user = user_collection.find_one({'email': email})
        if user is None:
            raise HTTPException(detail='User not found', status_code=404)
        if user['user_type'] != 'admin':
            raise HTTPException(detail='User is not Admin', status_code=400)
        return user

    @staticmethod
    async def get_email_from_token(authorization: str = Header(...)) -> str:
        """
        Returns email from JWT payload. Raises exception if token is invalid.
        :param authorization: Authorization token
        :return: email as a string from JWT payload
        """
        try:
            decode_token = Authentication.decode_jwt_token(authorization)
            email = decode_token["sub"]
        except KeyError as e:
            print(f"Error: {str(e)}")
            raise HTTPException(detail="Invalid token", status_code=400)
        return email

    @staticmethod
    def decode_jwt_token(token: str) -> Dict:
        """
        Decodes JWT token and returns payload if token is valid. Returns empty dict if token is invalid.
        :param token: Authorization token
        :return: dict including the payload data if token is valid otherwise an empty dict
        """
        try:
            token = token.split()[1]  # parsing the token
            payload = jwt.decode(token, Authentication.JWT_SECRET, algorithms=[Authentication.JWT_ALGORITHM])
            return payload
        except jwt.PyJWTError as e:
            print(e)
            return {}
