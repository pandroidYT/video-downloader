from flask import Flask, render_template, request, redirect, url_for, send_file
from flask import after_this_request
import yt_dlp
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            url = request.form['url']
            format_option = request.form.get('format', 'mp4')
            quality = request.form.get('quality', 'highest')

            # Create downloads directory if it doesn't exist
            if not os.path.exists('downloads'):
                os.makedirs('downloads')

            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',
                'paths': {'home': 'downloads'},
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
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if format_option == 'mp3':
                    filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                # Send file directly to user and then delete it
                file_path = os.path.join('downloads', filename)
                @after_this_request
                def remove_file(response):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing file: {e}")
                    return response
                
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename
                )

        except Exception as e:
            print(f"Error: {e}")
            return render_template('index.html', error=str(e))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
