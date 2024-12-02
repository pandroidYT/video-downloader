from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, Response
import yt_dlp
import os
import re
from urllib.parse import urlparse
import tempfile

app = Flask(__name__)

# Create a temporary directory for downloads
TEMP_DIR = tempfile.mkdtemp()

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_safe_filename(filename):
    # Remove invalid characters from filename
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def cleanup_old_files():
    # Clean up files older than 1 hour
    for filename in os.listdir(TEMP_DIR):
        filepath = os.path.join(TEMP_DIR, filename)
        try:
            if os.path.isfile(filepath) and (os.path.getctime(filepath) < (time.time() - 3600)):
                os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up {filepath}: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            url = request.form['url']
            format_option = request.form.get('format', 'mp4')
            quality = request.form.get('quality', 'highest')

            if not is_valid_url(url):
                raise ValueError("Invalid URL provided")

            # Clean up old files
            cleanup_old_files()

            def progress_hook(d):
                if d['status'] == 'downloading':
                    print(f"Downloading: {d.get('_percent_str', '0%')} of {d.get('_total_bytes_str', 'Unknown size')}")
                elif d['status'] == 'finished':
                    print(f"Download completed: {d.get('filename', 'Unknown file')}")

            ydl_opts = {
                'format': 'best' if format_option == 'mp4' else 'bestaudio',
                'progress_hooks': [progress_hook],
                'quiet': False,
                'no_warnings': True,
                'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                },
            }

            # Set format based on quality selection
            if format_option == 'mp4':
                if quality == 'highest':
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif quality == '720p':
                    ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
                elif quality == '480p':
                    ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
                else:  # 360p
                    ydl_opts['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best'
            elif format_option == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract video info first
                    print("Extracting video info...")
                    info = ydl.extract_info(url, download=False)
                    
                    if info.get('duration', 0) > 7200:  # 2 hours
                        raise ValueError("Video is too long (maximum 2 hours)")
                    
                    # Download the video
                    print("Starting download...")
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    if format_option == 'mp3':
                        filename = filename.rsplit('.', 1)[0] + '.mp3'
                    
                    filename = get_safe_filename(filename)
                    filepath = os.path.join(TEMP_DIR, filename)
                    
                    print(f"Download successful: {filename}")
                    
                    @after_this_request
                    def cleanup(response):
                        try:
                            os.remove(filepath)
                            print(f"Cleaned up file: {filepath}")
                        except Exception as e:
                            print(f"Error cleaning up {filepath}: {e}")
                        return response
                    
                    return send_file(
                        filepath,
                        as_attachment=True,
                        download_name=filename,
                        mimetype='audio/mpeg' if format_option == 'mp3' else 'video/mp4'
                    )

                except Exception as e:
                    error_msg = str(e)
                    print(f"Download error: {error_msg}")
                    if 'youtube' in url.lower():
                        error_msg = f"YouTube download error: {error_msg}. Please make sure the video is public and still available."
                    return jsonify({'error': error_msg}), 400

        except Exception as e:
            error_message = str(e)
            print(f"Error: {error_message}")
            return jsonify({'error': error_message}), 400

    return render_template('index.html')

if __name__ == '__main__':
    # Ensure temp directory exists
    os.makedirs(TEMP_DIR, exist_ok=True)
    # Get port from environment variable for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
