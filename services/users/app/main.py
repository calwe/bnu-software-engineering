from fastapi import FastAPI
from pydantic import BaseModel
import logging

logging.basicConfig(filename='myapp.log', level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class Login(BaseModel):
    username: str
    password: str

@app.post("/login/")
def read_root(login: Login):
    logger.info(f"User logged in: {login.username}")
    return { "message": "Logged In" }

