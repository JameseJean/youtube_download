from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 静态文件和模板配置
app.mount("/static", StaticFiles(directory="public/static"), name="static")
templates = Jinja2Templates(directory="templates")

# 创建下载目录
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# yt-dlp配置
ydl_opts = {
    'format': 'best',  # 最佳质量
    'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
    'quiet': True,
    'no_warnings': True,
}

async def get_video_info(url: str):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info["title"],
                "author": info["uploader"],
                "duration": info["duration"],
                "description": info.get("description", ""),
                "filename": ydl.prepare_filename(info)
            }
    except Exception as e:
        logger.error(f"获取视频信息错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/video-info")
async def get_info(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        if not url:
            return JSONResponse({"error": "需要URL"})
            
        logger.info(f"收到下载请求: {url}")
        result = await get_video_info(url)
        
        # 开始下载
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 返回文件路径供前端下载
        return JSONResponse({
            **result,
            "download_url": f"/download/{Path(result['filename']).name}"
        })
        
    except Exception as e:
        error_msg = f"处理请求错误: {str(e)}"
        logger.error(error_msg)
        return JSONResponse({"error": error_msg}, status_code=500)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = DOWNLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    ) 