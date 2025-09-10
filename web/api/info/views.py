from fastapi import APIRouter, Depends, Request
from utils.auth import verify
import tomllib

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="web/templates")

router = APIRouter(prefix="/info")


@router.get("/", dependencies=[Depends(verify)])
async def index(request: Request):
    with open("pyproject.toml", "rb") as f:
        version = tomllib.load(f)["project"]["version"]
    context = {"version": version}
    return templates.TemplateResponse(
        request=request, name="info.html", context=context
    )
