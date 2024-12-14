from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import yt_dlp
import os
import logging

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

async def get_video_info(url: str):
    ydl_opts = {
        'format': 'best',
        'no_warnings': True,
        'quiet': True
    }
    
    try:
        logger.info(f"开始获取视频信息: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                logger.error("未能获取视频信息")
                return {"error": "无法获取视频信息"}
                
            result = {
                "url": info.get('url'),
                "title": info.get('title'),
                "duration": info.get('duration'),
                "author": info.get('uploader'),
                "description": info.get('description')
            }
            logger.info(f"成功获取视频信息: {result['title']}")
            return result
            
    except Exception as e:
        error_msg = f"下载错误: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

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