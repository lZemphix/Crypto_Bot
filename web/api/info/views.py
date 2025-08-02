from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="web/templates")

router = APIRouter(prefix="/info")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="info.html")
