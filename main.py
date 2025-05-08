import os
import requests
import uuid
from flask import Flask, request, jsonify
from manim import *

# Set up Flask app
app = Flask(__name__)

# Directory to store rendered videos and frames
OUTPUT_DIR = "./rendered_videos"
FRAME_DIR = os.path.join(OUTPUT_DIR, "frames")
os.makedirs(FRAME_DIR, exist_ok=True)

def render_lottie_to_images(lottie_url):
    # Step 1: Fetch the Lottie JSON
    response = requests.get(lottie_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch Lottie JSON.")

    # Step 2: Save the Lottie JSON to a temporary file
    lottie_json_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.json")
    with open(lottie_json_path, 'w') as f:
        f.write(response.text)
    
    # Step 3: Render the Lottie animation using Manim
    print("Rendering Lottie frames...")
    os.makedirs(FRAME_DIR, exist_ok=True)
    
    # Manim command to render Lottie JSON frames (you can customize this)
    # You can replace this with a proper Lottie frame rendering process
    for i in range(30):  # Simulate 30 frames (adjust as needed)
        frame_image = os.path.join(FRAME_DIR, f"frame_{i}.png")
        os.system(f"convert -size 500x500 xc:white {frame_image}")  # Placeholder (white image)
    
    # Verify frames are generated
    frame_count = len(os.listdir(FRAME_DIR))
    if frame_count == 0:
        raise Exception("No frames generated. Frame rendering failed.")

    print(f"Generated {frame_count} frames.")
    return FRAME_DIR

def convert_images_to_mp4():
    print("Converting frames to MP4...")
    mp4_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp4")
    
    # Direct FFmpeg command
    command = f"ffmpeg -framerate 24 -i {FRAME_DIR}/frame_%d.png -pix_fmt yuv420p {mp4_path} -y"
    print("Running FFmpeg Command:", command)
    
    result = os.system(command)
    print("FFmpeg Result Code:", result)
    
    # Check if MP4 was created
    if not os.path.exists(mp4_path):
        raise Exception("FFmpeg failed to create MP4. Check frame directory and ffmpeg command.")
    
    print(f"MP4 generated: {mp4_path}")
    return mp4_path

@app.route('/convert', methods=['POST'])
def convert_lottie_to_mp4():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
