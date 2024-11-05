import time
import os
import jwt

from typing import Dict
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

JWT_SECRET = os.getenv("secret")
JWT_ALGORITHM = os.getenv("algorithm")

def token_response(token: str):
    return {
        "access_token": token
    }

def sign_jwt(user_id : str) -> Dict[str, str]:

    payload={
        "user_id" : user_id,
        "expires" : time.time() + 3600 #delay avant expriration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}


        
