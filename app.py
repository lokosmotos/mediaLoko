import os
import uuid
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def burn_subtitles(video_path, srt_path, output_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles={srt_path}",
        '-c:a', 'copy',
        output_path
    ]
    subprocess.run(command, check=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video = request.files['video']
        srt = request.files['srt']
        if not video or not srt:
            flash("Please upload both video and subtitle files")
            return redirect(url_for('index'))

        video_filename = secure_filename(video.filename)
        srt_filename = secure_filename(srt.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{video_filename}")
        srt_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{srt_filename}")
        output_path = video_path.replace('.mp4', '_subtitled.mp4')

        video.save(video_path)
        srt.save(srt_path)

        try:
            burn_subtitles(video_path, srt_path, output_path)
        except Exception as e:
            flash(f"Error: {e}")
            return redirect(url_for('index'))

        return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(output_path), as_attachment=True)

    return render_template('index.html')

