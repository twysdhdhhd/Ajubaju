import os
import requests
import uuid
from flask import Flask, request, jsonify, send_from_directory
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Set up Flask app
app = Flask(__name__)

# Directory to store rendered videos and frames
OUTPUT_DIR = "./rendered_videos"
FRAME_DIR = os.path.join(OUTPUT_DIR, "frames")
os.makedirs(FRAME_DIR, exist_ok=True)

# Download and use a portable version of Chromium
CHROMIUM_PATH = "/opt/render/project/.chromium/chrome-linux/chrome"

def setup_chromium():
    """Ensure Chromium is downloaded and available."""
    if not os.path.exists(CHROMIUM_PATH):
        os.makedirs("/opt/render/project/.chromium/chrome-linux", exist_ok=True)
        print("Downloading Chromium...")
        os.system("wget https://commondatastorage.googleapis.com/chromium-browser-snapshots/Linux_x64/1058845/chrome-linux.zip -O /opt/render/project/.chromium/chrome-linux.zip")
        os.system("unzip /opt/render/project/.chromium/chrome-linux.zip -d /opt/render/project/.chromium/")
        print("Chromium downloaded.")

def cleanup_old_videos():
    """Automatically delete videos older than 1 minute."""
    current_time = time.time()
    for filename in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > 60:  # 1 minute (60 seconds)
                os.remove(file_path)
                print(f"Deleted old video: {filename}")

def render_lottie_to_images(lottie_url):
    """Download and render Lottie JSON directly from the URL using headless Chrome."""
    print("Rendering Lottie frames...")
    os.makedirs(FRAME_DIR, exist_ok=True)
    setup_chromium()  # Ensure Chromium is available

    # Set up headless Chrome with custom path
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=500,500")
    chrome_options.binary_location = CHROMIUM_PATH
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get(lottie_url)
    
    frame_count = 30  # Capture 30 frames (adjust as needed)
    for frame_number in range(frame_count):
        frame_image = os.path.join(FRAME_DIR, f"frame_{frame_number}.png")
        driver.save_screenshot(frame_image)
        print(f"Captured frame {frame_number + 1}/{frame_count}")
    
    driver.quit()
    print("Frames rendered successfully.")

def convert_images_to_mp4():
    """Convert rendered frames to an MP4 using ffmpeg."""
    print("Converting frames to MP4...")
    mp4_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp4")
    
    # Direct FFmpeg command
    command = f"ffmpeg -framerate 30 -i {FRAME_DIR}/frame_%d.png -pix_fmt yuv420p {mp4_path} -y"
    print("Running FFmpeg Command:", command)
    
    os.system(command)
    
    if not os.path.exists(mp4_path):
        raise Exception("FFmpeg failed to create MP4. Check frame directory and ffmpeg command.")
    
    print(f"MP4 generated: {mp4_path}")
    return mp4_path

@app.route('/convert', methods=['POST'])
def convert_lottie_to_mp4():
    """Convert a Lottie JSON URL to an MP4 file."""
    cleanup_old_videos()  # Clean up old videos before creating a new one
    
    data = request.get_json()
    lottie_url = data.get('lottie_url')

    if not lottie_url:
        return jsonify({'error': 'Lottie URL is required'}), 400

    try:
        # Step 1: Render Lottie to images
        render_lottie_to_images(lottie_url)

        # Step 2: Convert images to MP4
        mp4_path = convert_images_to_mp4()

        # Clean up frames after conversion
        for file in os.listdir(FRAME_DIR):
            os.remove(os.path.join(FRAME_DIR, file))

        # Return the URL to access the MP4 file
        return jsonify({'mp4_url': request.host_url + 'rendered_videos/' + os.path.basename(mp4_path)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rendered_videos/<filename>')
def serve_video(filename):
    """Serve rendered MP4 videos."""
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
