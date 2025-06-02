import os

from dotenv import load_dotenv
from fastapi import FastAPI
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

app = FastAPI()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)
