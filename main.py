from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
import yt_dlp
import asyncio
import json
import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取环境变量
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "downloads"))
MAX_DOWNLOADS = int(os.getenv("MAX_DOWNLOADS", 10))
IS_VERCEL = os.getenv("VERCEL", False)

# 创建下载目录
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 根据环境配置静态文件
if not IS_VERCEL:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="public/static"), name="static")

def get_video_info(url: str):
    with yt_dlp.YoutubeDL() as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info["title"],
                "duration": info["duration"],
                "author": info["uploader"],
                "description": info["description"],
                "thumbnail": info["thumbnail"]
            }
        except Exception as e:
            return {"error": str(e)}

async def download_video(url: str, video_id: str, websocket: WebSocket):
    def progress_hook(d):
        if d['status'] == 'downloading':
            progress = {
                'status': 'downloading',
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes', 0),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0)
            }
            asyncio.create_task(websocket.send_json(progress))
        elif d['status'] == 'finished':
            progress = {'status': 'finished'}
            asyncio.create_task(websocket.send_json(progress))

    ydl_opts = {
        'format': 'best',
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            downloads[video_id] = {
                "title": info["title"],
                "duration": info["duration"],
                "author": info["uploader"],
                "description": info["description"],
                "path": str(DOWNLOAD_DIR / f"{info['title']}.{info['ext']}")
            }
            # 保存下载记录
            with open("downloads.json", "w") as f:
                json.dump(downloads, f)
    except Exception as e:
        await websocket.send_json({"error": str(e)})

@app.get("/")
async def home(request: Request):
    # 读取已下载视频列表
    try:
        with open("downloads.json") as f:
            downloads = json.load(f)
    except:
        downloads = {}
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "downloads": downloads}
    )

@app.post("/video-info")
async def get_info(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return JSONResponse({"error": "URL is required"})
    return JSONResponse(get_video_info(url))

async def get_video_url(url: str):
    ydl_opts = {
        'format': 'best',  # 获取最佳质量
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # 只获取信息，不下载
            return {
                "url": info.get('url'),  # 直接返回视频URL
                "title": info.get('title'),
                "duration": info.get('duration'),
                "author": info.get('uploader'),
                "description": info.get('description')
            }
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/download/{video_id}")
async def websocket_endpoint(websocket: WebSocket, video_id: str):
    await websocket.accept()
    data = await websocket.receive_json()
    url = data.get("url")
    
    if not url:
        await websocket.send_json({"error": "URL is required"})
        return
        
    # 获取视频信息和直接下载链接
    video_info = await get_video_url(url)
    if "error" in video_info:
        await websocket.send_json({"error": video_info["error"]})
        return
        
    # 返回视频信息和下载链接
    await websocket.send_json({
        "status": "ready",
        "download_url": video_info["url"],
        "info": {
            "title": video_info["title"],
            "duration": video_info["duration"],
            "author": video_info["author"],
            "description": video_info["description"]
        }
    }) 