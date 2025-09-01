from fastapi import APIRouter, Depends, Request
from utils.auth import verify

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="web/templates")

router = APIRouter(prefix="/info")


@router.get("/", dependencies=[Depends(verify)])
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="info.html")
