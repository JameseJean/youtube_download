# YouTube 视频下载器

一个简单的YouTube视频下载工具，基于FastAPI + yt-dlp实现。在本地运行，支持视频下载到本地观看。

## 功能特点

- 支持输入YouTube视频链接直接下载到本地
- 实时显示下载进度
- 显示视频详细信息（标题、作者、时长等）
- 保存下载历史记录
- 响应式界面设计

## 技术栈

- 后端: FastAPI + yt-dlp
- 前端: TailwindCSS + 原生JavaScript
- 实时通信: WebSocket
- 本地存储: LocalStorage (下载历史)

## 本地运行

1. 克隆项目
```bash
git clone https://github.com/your-username/youtube-downloader.git
cd youtube-downloader
```

2. 安装依赖
```bash
pip install fastapi uvicorn python-multipart yt-dlp websockets jinja2
```

3. 运行服务器
```bash
python -m uvicorn main:app --reload
```

4. 访问 http://localhost:8000 开始使用

## 项目结构

- `public/static/`: 静态文件目录
  - `css/`: 样式文件
  - `js/`: JavaScript文件
- `templates/`: HTML模板文件
- `downloads/`: 下载的视频存储目录
- `main.py`: 后端主程序

## 使用说明

1. 在输入框中粘贴YouTube视频链接
2. 点击下载按钮
3. 等待下载完成
4. 视频将保存在本地downloads目录
5. 可在页面下方查看下载历史

## 注意事项

- 确保有足够的磁盘空间存储下载的视频
- 下载历史保存在浏览器本地存储中
- 支持的视频格式取决于yt-dlp的支持情况

