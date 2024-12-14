# YouTube 视频下载器

一个简单的YouTube视频下载工具，基于FastAPI + yt-dlp实现。支持本地开发和Vercel部署。

## 功能特点

- 支持输入YouTube视频链接直接下载
- 实时显示下载进度
- 显示视频详细信息
- 支持视频格式选择
- 响应式界面设计

## 技术栈

- 后端: FastAPI + yt-dlp
- 前端: TailwindCSS + 原生JavaScript
- 实时通信: WebSocket
- 部署: Vercel

## 本地开发

1. 克隆项目
bash
git clone https://github.com/your-username/youtube-downloader.git
cd youtube-downloader

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 创建 .env 文件
```bash
DOWNLOAD_DIR=downloads
MAX_DOWNLOADS=10
```

4. 运行开发服务器
```bash
uvicorn main:app --reload
```

5. 访问 http://localhost:8000

## Vercel部署

1. Fork 本项目到你的GitHub账号

2. 在Vercel中导入项目

3. 设置环境变量:
   - DOWNLOAD_DIR: downloads
   - MAX_DOWNLOADS: 10

4. 部署完成后即可使用

## 项目结构说明

- `public/static/`: 静态文件目录
  - 本地开发和Vercel部署共用此目录
  - CSS、JavaScript等静态资源放在这里
- `templates/`: 模板文件目录
- `main.py`: 后端主程序
- `vercel.json`: Vercel部署配置

## 注意事项

- 本地开发时静态文件通过FastAPI的StaticFiles服务
- Vercel部署时静态文件由Vercel平台处理
- 两种环境下静态文件路径保持一致(/static/...)

