from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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

# 创建下载目录
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

@app.websocket("/ws/download/{video_id}")
async def websocket_endpoint(websocket: WebSocket, video_id: str):
    await websocket.accept()
    data = await websocket.receive_json()
    url = data.get("url")
    if not url:
        await websocket.send_json({"error": "URL is required"})
        return
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            progress = {
                'status': 'downloading',
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes', 0),
                'eta': d.get('eta', 0)
            }
            asyncio.create_task(websocket.send_json(progress))
        elif d['status'] == 'finished':
            progress = {'status': 'finished'}
            asyncio.create_task(websocket.send_json(progress))

    ydl_opts = {
        'format': 'best',
        'progress_hooks': [progress_hook],
        # 修改为用户下载目录
        'outtmpl': '%(title)s.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            # 返回下载链接而不是保存到服务器
            video_url = info.get('url')
            await websocket.send_json({
                'status': 'ready',
                'download_url': video_url,
                'info': {
                    "title": info["title"],
                    "duration": info["duration"],
                    "author": info["uploader"],
                    "description": info["description"]
                }
            })
    except Exception as e:
        await websocket.send_json({"error": str(e)}) 