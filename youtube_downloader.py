import yt_dlp


def download_video(url, output_path='.'):
    try:
        # Set options for yt-dlp
        ydl_opts = {
            'format': 'best',  # Download best quality
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Output file template
        }

        # Download video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("Download completed!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_video(video_url)
