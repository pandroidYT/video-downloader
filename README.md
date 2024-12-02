# Video Downloader

A web-based video downloader that supports multiple platforms including YouTube, Instagram, and Facebook. Built with Python, Flask, and yt-dlp.

## Features

- Download videos from:
  - YouTube
  - Instagram
  - Facebook
- Multiple format options:
  - MP4 video
  - MP3 audio
- Quality selection:
  - Best quality
  - 720p
  - 480p
  - 360p
- Clean, modern interface
- Progress tracking
- Error handling

## Requirements

- Python 3.8+
- Flask
- yt-dlp
- FFmpeg (for audio conversion)

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd video-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
- Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

## Usage

1. Run the application:
```bash
python app.py
```

2. Open your browser and go to `http://localhost:5000`
3. Paste a video URL and select your preferred format and quality
4. Click Download

## License

MIT License
