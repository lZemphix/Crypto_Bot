from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv, set_key

load_dotenv()

templates = Jinja2Templates(directory="web/templates")

router = APIRouter(prefix="/statistic")


@router.get("/")
async def settings(request: Request):
    raise HTTPException(
        status_code=401,
    )
    # return templates.TemplateResponse(request=request, name='statistic.html')
