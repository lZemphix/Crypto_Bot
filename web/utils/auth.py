import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

security = HTTPBasic()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

async def verify(creds: HTTPBasicCredentials = Depends(security)):
    if creds.password != PASSWORD or creds.username != USERNAME:
        raise HTTPException(
            status_code=401,
            detail='Incorrect password or username'
        )
    return True