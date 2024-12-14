from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import yt_dlp
import os
import logging
import random
import json
from typing import Optional, Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 根据环境配置静态文件
IS_VERCEL = os.getenv("VERCEL", False)
if not IS_VERCEL:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="public/static"), name="static")

# 浏览器标识池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
]

def get_random_headers() -> Dict[str, str]:
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Referer': 'https://www.youtube.com/'
    }

async def get_video_info(url: str):
    ydl_opts = {
        'format': 'best',
        'no_warnings': True,
        'quiet': True,
        'extract_flat': True,
        'http_headers': get_random_headers()
    }
    
    try:
        logger.info(f"开始获取视频信息: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except yt_dlp.utils.ExtractorError as e:
                if "Sign in to confirm your age" in str(e):
                    raise HTTPException(status_code=403, detail="需要年龄验证，无法下载")
                elif "requested format not available" in str(e):
                    raise HTTPException(status_code=404, detail="请求的视频格式不可用")
                else:
                    raise HTTPException(status_code=500, detail=str(e))
                    
            if not info:
                raise HTTPException(status_code=404, detail="无法获取视频信息")
                
            result = {
                "url": info.get('url'),
                "title": info.get('title'),
                "duration": info.get('duration'),
                "author": info.get('uploader'),
                "description": info.get('description'),
                "formats": info.get('formats', [])  # 添加格式选项
            }
            return result
            
    except Exception as e:
        error_msg = f"下���错误: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/video-info")
async def get_info(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        if not url:
            return JSONResponse({"error": "URL is required"})
            
        logger.info(f"收到下载请求: {url}")
        result = await get_video_info(url)
        return JSONResponse(result)
        
    except Exception as e:
        error_msg = f"处理请求错误: {str(e)}"
        logger.error(error_msg)
        return JSONResponse({"error": error_msg}, status_code=500) 