from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import yt_dlp
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 根据环境配置静态文件
IS_VERCEL = os.getenv("VERCEL", False)
if not IS_VERCEL:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="public/static"), name="static")

async def get_video_info(url: str):
    ydl_opts = {
        'format': 'best',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "url": info.get('url'),
                "title": info.get('title'),
                "duration": info.get('duration'),
                "author": info.get('uploader'),
                "description": info.get('description')
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/video-info")
async def get_info(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return JSONResponse({"error": "URL is required"})
    return JSONResponse(await get_video_info(url)) 