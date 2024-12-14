// 保存下载历史
function saveToHistory(videoInfo) {
    const history = JSON.parse(localStorage.getItem('downloadHistory') || '[]');
    history.unshift({  // 新的记录放在前面
        title: videoInfo.title,
        author: videoInfo.author,
        duration: videoInfo.duration,
        description: videoInfo.description,
        date: new Date().toISOString()
    });
    // 只保留最近20条记录
    if (history.length > 20) history.pop();
    localStorage.setItem('downloadHistory', JSON.stringify(history));
}

// 显示下载历史
function showDownloadHistory() {
    const history = JSON.parse(localStorage.getItem('downloadHistory') || '[]');
    const historyContainer = document.getElementById('download-history');
    
    if (history.length === 0) {
        historyContainer.innerHTML = '<p class="text-gray-500">暂无下载记录</p>';
        return;
    }

    const historyHTML = history.map(item => `
        <div class="bg-white rounded-lg shadow-md p-4 mb-4">
            <h3 class="font-bold text-lg mb-1">${item.title}</h3>
            <p class="text-gray-600 text-sm">作者: ${item.author}</p>
            <p class="text-gray-600 text-sm">时长: ${item.duration}秒</p>
            <p class="text-gray-600 text-sm">下载时间: ${new Date(item.date).toLocaleString()}</p>
        </div>
    `).join('');
    
    historyContainer.innerHTML = historyHTML;
}

// 下载带进度显示的函数
async function downloadWithProgress(url) {
    const progress = document.getElementById('progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    progress.classList.remove('hidden');
    
    try {
        const response = await fetch(url);
        const contentLength = response.headers.get('content-length');
        const total = parseInt(contentLength, 10);
        const reader = response.body.getReader();
        
        let receivedLength = 0;
        
        while(true) {
            const {done, value} = await reader.read();
            
            if (done) {
                progressText.textContent = '下载完成!';
                setTimeout(() => progress.classList.add('hidden'), 1000);
                break;
            }
            
            receivedLength += value.length;
            const percent = (receivedLength / total) * 100;
            progressBar.style.width = `${percent}%`;
            progressText.textContent = `下载中: ${percent.toFixed(1)}%`;
        }
    } catch (error) {
        console.error('下载错误:', error);
        progressText.textContent = '下载失败';
        setTimeout(() => progress.classList.add('hidden'), 1000);
    }
}

// 主下载函数
async function startDownload() {
    const url = document.getElementById('url').value;
    if (!url) return;

    try {
        const response = await fetch('/video-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({url: url})
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }

        // 显示视频信息
        const videoInfo = document.getElementById('video-info');
        videoInfo.classList.remove('hidden');
        document.getElementById('video-title').textContent = data.title;
        document.getElementById('video-author').textContent = `作者: ${data.author}`;
        document.getElementById('video-duration').textContent = `时长: ${data.duration}秒`;
        document.getElementById('video-description').textContent = data.description;
        
        // 保存到历史记录
        saveToHistory(data);
        
        // 开始下载并显示进度
        await downloadWithProgress(data.url);
        
        // 刷新历史记录显示
        showDownloadHistory();
        
    } catch (error) {
        console.error('下载错误:', error);
        alert('下载出错');
    }
}

// 页面加载时显示历史记录
window.addEventListener('load', showDownloadHistory); 