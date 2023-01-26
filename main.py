from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from settings import templates
from okr_helper import okr_router


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(okr_router)


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("base/index.html", {"request": request})
