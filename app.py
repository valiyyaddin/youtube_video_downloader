from flask import Flask, request, send_file, jsonify, render_template
from pytube import YouTube
import os
from uuid import uuid4
from flask_cors import CORS

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

    if not url or not quality:
        return jsonify({"error": "Missing URL or quality"}), 400

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp', res=quality).first()

        if not stream:
            return jsonify({"error": f"{quality} not available."}), 404

        filename = f"{uuid4().hex}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)

        return send_file(filepath, as_attachment=True, download_name=yt.title + ".mp4")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
