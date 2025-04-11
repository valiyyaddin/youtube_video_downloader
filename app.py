from flask import Flask, request, send_file, jsonify, render_template, after_this_request
import os
from uuid import uuid4
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")
    quality = data.get("quality")
    video_filename = f"{uuid4().hex}-{quality}.mp4"

    if not url or not quality:
        return jsonify({"error": "Missing URL or quality"}), 400

    try:
        # Configure yt_dlp options
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, video_filename),
            'merge_output_format': 'mp4'
        }

        # Download video using yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title')
            filepath = os.path.join(DOWNLOAD_FOLDER, video_filename)

        # Ensure file is deleted after the response is sent
        @after_this_request
        def cleanup_file(response):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)  # Delete the file
            except Exception as e:
                print(f"Error deleting file: {e}")
            return response

        # Send the downloaded file to the client
        return send_file(filepath, as_attachment=True, download_name=f"{video_title}-{quality}p.mp4")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)