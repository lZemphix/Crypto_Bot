import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.index.views import router as index_router
from api.settings.views import router as settings_router
from api.info.views import router as info_router
from api.statistic.views import router as statistic_router
from api.auth.views import router as auth_router

import uvicorn

app = FastAPI()

app.include_router(index_router)
app.include_router(settings_router)
app.include_router(info_router)
app.include_router(statistic_router)
app.include_router(auth_router)


current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=10605, host="0.0.0.0")
