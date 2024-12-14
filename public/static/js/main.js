// 这个函数已经在 index.html 中定义，可以移动到这里
async function startDownload() {
    const url = document.getElementById('url').value;
    if (!url) return;

    // 显示进度条
    const progress = document.getElementById('progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    progress.classList.remove('hidden');

    // 生成随机ID
    const videoId = Math.random().toString(36).substring(7);

    // 创建WebSocket连接
    const ws = new WebSocket(`ws://${window.location.host}/ws/download/${videoId}`);
    
    ws.onopen = () => {
        ws.send(JSON.stringify({url: url}));
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.error) {
            alert(data.error);
            progress.classList.add('hidden');
            return;
        }

        if (data.status === 'downloading') {
            const percent = (data.downloaded_bytes / data.total_bytes * 100).toFixed(1);
            progressBar.style.width = `${percent}%`;
            progressText.textContent = `下载中: ${percent}% - 剩余时间: ${data.eta}秒`;
        }

        if (data.status === 'ready') {
            // 显示视频信息
            const videoInfo = document.getElementById('video-info');
            videoInfo.classList.remove('hidden');
            document.getElementById('video-title').textContent = data.info.title;
            document.getElementById('video-author').textContent = `作者: ${data.info.author}`;
            document.getElementById('video-duration').textContent = `时长: ${data.info.duration}秒`;
            document.getElementById('video-description').textContent = data.info.description;
            
            // 开始下载
            window.location.href = data.download_url;
        }

        if (data.status === 'finished') {
            progressText.textContent = '下载完成!';
            setTimeout(() => {
                progress.classList.add('hidden');
            }, 1000);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
        alert('下载出错');
        progress.classList.add('hidden');
    };
} 