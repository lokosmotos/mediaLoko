import os
import uuid
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import subprocess
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB limit

# Allowed file extensions
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov'}
ALLOWED_SRT_EXTENSIONS = {'srt'}

# Create uploads directory if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to check allowed extensions
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Function to burn subtitles into the video
def burn_subtitles(video_path, srt_path, output_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles={srt_path}",
        '-c:a', 'copy',
        output_path
    ]

    try:
        # Capture stdout and stderr
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("FFmpeg output:", result.stdout)
        print("FFmpeg errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed!")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        print("Output:", e.output)
        print("Error:", e.stderr)
        raise RuntimeError(f"FFmpeg error: {e.stderr}")

# Background thread to process the video
def background_ffmpeg(video_path, srt_path, output_path):
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'subtitles={srt_path}',
            '-c:a', 'copy',
            output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed:", e.stderr)

# Main route to handle file uploads and processing
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if files are provided
        video = request.files['video']
        srt = request.files['srt']
        
        if not video or not srt:
            flash("Please upload both video and subtitle files.")
            return redirect(url_for('index'))

        # Validate file extensions
        if not allowed_file(video.filename, ALLOWED_VIDEO_EXTENSIONS):
            flash("Invalid video file type. Only MP4, MKV, AVI, and MOV are allowed.")
            return redirect(url_for('index'))

        if not allowed_file(srt.filename, ALLOWED_SRT_EXTENSIONS):
            flash("Invalid subtitle file type. Only SRT files are allowed.")
            return redirect(url_for('index'))

        # Generate secure filenames
        video_filename = secure_filename(video.filename)
        srt_filename = secure_filename(srt.filename)
        
        # Create paths for the uploaded video and SRT
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{video_filename}")
        srt_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{srt_filename}")
        
        # Define the output file path (subtitled video)
        output_filename = f"{uuid.uuid4()}_{video_filename.rsplit('.', 1)[0]}_subtitled.mp4"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Save video and subtitle files
        video.save(video_path)
        srt.save(srt_path)

        try:
            # Burn subtitles into the video
            burn_subtitles(video_path, srt_path, output_path)
        except Exception as e:
            flash(f"Error: {e}")
            return redirect(url_for('index'))

        # Send the output file for download
        return send_from_directory(app.config['UPLOAD_FOLDER'], output_filename, as_attachment=True)

    return render_template('index.html')

if __name__ == "__main__":
    # Get the port from environment variable, default to 5000 if not set
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
