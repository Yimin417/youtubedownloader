# YouTube Video Downloader / YouTube视频下载器

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A modern, feature-rich desktop application for downloading YouTube videos and playlists**

**现代化、功能丰富的桌面应用程序，用于下载YouTube视频和播放列表**

</div>

---

## 📋 Features / 功能特性

### English
- **High-quality downloads** - Support for up to 8K resolution (144p to 8K)
- **Multiple video formats** - MP4, WebM, MKV
- **Audio extraction** - Convert to MP3 (320kbps) with audio-only mode
- **Playlist support** - Download entire YouTube playlists
- **Subtitle download** - Download subtitles in multiple languages with optional embedding (requires FFmpeg)
- **Progress tracking** - Real-time download progress with speed and ETA
- **Download history** - Track recent downloads (configurable limit, default 10)
- **Dark/Light themes** - Switch between appearance modes
- **Settings panel** - Configure download path, history limit, auto-exit option

### 中文
- **高质量下载** - 支持从144p到8K全分辨率
- **多种视频格式** - MP4、WebM、MKV
- **音频提取** - 仅音频模式转换为MP3（320kbps）
- **播放列表支持** - 下载完整的YouTube播放列表
- **字幕下载** - 下载多语言字幕，可选嵌入视频（需FFmpeg）
- **进度跟踪** - 实时显示下载进度、速度和剩余时间
- **下载历史** - 记录下载历史（可配置数量，默认10条）
- **深色/浅色主题** - 切换界面外观
- **设置面板** - 配置下载路径、历史限制、自动退出选项

---

## 📦 Requirements / 系统要求

### English
- **Python 3.8+**
- **FFmpeg** (recommended for merging video+audio streams and subtitle embedding)

### 中文
- **Python 3.8+**
- **FFmpeg**（推荐用于合并音视频流和嵌入字幕）

---

## 🚀 Installation / 安装步骤

### English

#### 1. Clone or download this repository
```bash
cd downloader
```

#### 2. Create virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install FFmpeg (recommended)

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract and add `bin` folder to PATH environment variable
3. Restart terminal

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
```

**macOS:**
```bash
brew install ffmpeg
```

### 中文

#### 1. 克隆或下载本仓库
```bash
cd downloader
```

#### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 安装 FFmpeg（推荐）

**Windows:**
1. 从 https://ffmpeg.org/download.html 下载
2. 解压并将 `bin` 文件夹添加到 PATH 环境变量
3. 重启终端

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
```

**macOS:**
```bash
brew install ffmpeg
```

---

## 🔧 Usage / 使用方法

### English

#### Launch the Application
```bash
# Using the main script
python main.py

# Or from within the virtual environment
venv\Scripts\python main.py

# Or as a module
python -m src
```

#### Basic Workflow
1. **Enter URL** - Paste a YouTube video or playlist URL
2. **Configure options** - Select resolution, format, and additional options (subtitles, embed)
3. **Download** - Click "Download" to start
4. **Monitor** - Watch progress in real-time with speed and ETA
5. **View history** - Check the download history section for past downloads

#### Available Options
| Option | Description |
|--------|-------------|
| Resolution | Target video quality (144p - 8K) |
| Format | Container format for video (MP4, WebM, MKV) |
| Audio Only | Extract audio as MP3 (320kbps) |
| Download Subtitles | Download subtitle files in available languages |
| Embed Subtitles | Burn subtitles into video (requires FFmpeg) |

### 中文

#### 启动应用
```bash
# 使用主脚本
python main.py

# 或在虚拟环境中
venv\Scripts\python main.py

# 或作为模块运行
python -m src
```

#### 基本流程
1. **输入URL** - 粘贴YouTube视频或播放列表链接
2. **配置选项** - 选择分辨率、格式和其他选项（字幕、嵌入等）
3. **开始下载** - 点击"Download"开始下载
4. **实时监控** - 查看实时进度、速度和剩余时间
5. **查看历史** - 在历史记录部分查看过往下载

#### 可用选项
| 选项 | 描述 |
|------|------|
| 分辨率 | 目标视频质量（144p - 8K） |
| 格式 | 视频容器格式（MP4、WebM、MKV） |
| 仅音频 | 提取音频为MP3（320kbps） |
| 下载字幕 | 获取可用语言的字幕文件 |
| 嵌入字幕 | 将字幕烧录到视频（需要FFmpeg） |

---

## 📁 Project Structure / 项目结构

```
downloader/
├── src/
│   ├── downloader/
│   │   ├── engine.py      # Core yt-dlp wrapper / 核心yt-dlp封装
│   │   ├── formats.py     # Format management / 格式管理
│   │   ├── progress.py    # Progress tracking & history / 进度跟踪和历史
│   │   └── __init__.py
│   ├── gui/
│   │   ├── main.py        # Main GUI application / 主GUI应用
│   │   ├── theme.py       # Theme configuration / 主题配置
│   │   └── __init__.py
│   ├── utils/
│   │   ├── config.py      # Configuration management / 配置管理
│   │   ├── logger.py      # Logging utilities / 日志工具
│   │   └── __init__.py
│   └── __init__.py
├── assets/
│   └── icons/             # Application icons (optional) / 应用图标（可选）
├── venv/                  # Virtual environment (auto-created) / 虚拟环境（自动创建）
├── main.py                # Entry point script / 入口点脚本
├── requirements.txt       # Python dependencies / Python依赖
├── config.json            # User configuration (auto-created) / 用户配置（自动创建）
├── LICENSE                # MIT License / MIT许可证
└── README.md              # This file / 本文件
```

---

## ⚙️ Configuration / 配置

Configuration is stored in `config.json` (auto-created on first run):

配置文件存储在 `config.json`（首次运行自动创建）：

```json
{
  "default_download_path": "C:\\Users\\Username\\Downloads\\YouTube",
  "default_resolution": "1080",
  "default_format": "mp4",
  "download_subtitles": false,
  "subtitle_languages": ["en"],
  "embed_subtitles": false,
  "download_thumbnail": true,      // Reserved for future use / 保留字段（未来功能）
  "theme": "dark",
  "history_limit": 10,
  "auto_exit": false
}
```

**Note**: The `download_thumbnail` option is currently reserved and not used by the GUI. Thumbnail downloads are disabled for performance reasons.

**注意**：`download_thumbnail` 选项当前为保留字段，GUI未提供控制。缩略图下载功能已禁用以提高性能。

---
---

## 🔧 Troubleshooting / 故障排除

### GUI doesn't start / TclError
- Ensure Tkinter is available: `python -m tkinter`
- On Linux: `sudo apt install python3-tk`
- On macOS: Tkinter is included with Python from python.org

### Download fails with "unsupported url"
- Check the URL is valid and accessible
- Ensure yt-dlp is up-to-date: `pip install -U yt-dlp`
- Some videos may be age-restricted or region-locked

### No video formats available / 403 errors
- Update yt-dlp: `pip install -U yt-dlp`
- Some platforms may require cookies or authentication

### FFmpeg not found (when embedding subtitles/merging streams)
- Install FFmpeg and add to PATH
- See Installation section above

### Downloads are slow
- Check your internet connection
- Some servers limit download speed
- Try lower resolution

---

## 💻 Advanced Usage / 高级用法

### Programmatic Usage / 编程使用

```python
from downloader.engine import DownloadEngine

engine = DownloadEngine(download_path="/path/to/downloads")
engine.set_progress_callback(lambda p: print(f"{p.progress:.1f}% - {p.speed}"))

success = engine.download(
    url="https://youtube.com/watch?v=example",
    resolution="1080",
    output_format="mp4",
    download_subtitles=True,
    subtitle_langs=["en", "zh"],
    embed_subtitle=False,        # Set to True to embed subtitles (requires FFmpeg)
    download_thumbnail=False    # Thumbnail download currently disabled
)

# For playlist downloads with range:
success = engine.download(
    url="https://youtube.com/playlist?list=...",
    resolution="1080",
    output_format="mp4",
    playlist_start=1,    # Start from first video
    playlist_end=10      # Download first 10 videos only
)
```

---

## 🤝 Contributing / 贡献

We welcome contributions! Please follow these steps:

我们欢迎贡献！请按以下步骤：

1. **Fork the repository** / 复制仓库
2. **Create a feature branch** / 创建功能分支
3. **Make your changes** / 进行修改
4. **Submit a Pull Request** / 提交Pull Request

---

## 📄 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用 MIT 许可证 - 详细信息请查看 [LICENSE](LICENSE) 文件。

---

## 🙏 Credits / 致谢

- **yt-dlp** - YouTube download engine (https://github.com/yt-dlp/yt-dlp)
- **CustomTkinter** - Modern Tkinter widgets (https://github.com/TomSchimansky/CustomTkinter)
- **FFmpeg** - Video/audio processing (https://ffmpeg.org/)

---

## ⚠️ Disclaimer / 免责声明

**English**: This software is for personal use only. Please respect YouTube's Terms of Service and content creators' rights. Only download content you have permission to download. The authors are not responsible for any misuse of this software.

**中文**: 本软件仅供个人使用。请尊重YouTube的服务条款和内容创作者的权利。仅下载您有权限下载的内容。作者不对本软件的任何滥用行为负责。

---

<div align="center">
Made with ❤️ using Python, CustomTkinter & yt-dlp
</div>
