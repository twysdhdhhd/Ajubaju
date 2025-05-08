import os
import requests
import uuid
from flask import Flask, request, jsonify
from manim import *

# Set up Flask app
app = Flask(__name__)

# Directory to store rendered videos
OUTPUT_DIR = "./rendered_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    # You may need to adjust this part to suit your Lottie JSON and animation
    frame_dir = os.path.join(OUTPUT_DIR, "frames")
    os.makedirs(frame_dir, exist_ok=True)
    
    # Manim command to render Lottie JSON frames (adjust this according to how Lottie should be rendered)
    command = f"manim -pql --disable_caching {lottie_json_path} --frame_width=500 --frame_height=500"
    
    # Run the command to generate frames using Manim
    os.system(command)

    # Return the list of rendered frames
    frame_paths = [os.path.join(frame_dir, f"frame_{i}.png") for i in range(len(os.listdir(frame_dir)))]
    
    return frame_paths

def convert_images_to_mp4(frame_paths):
    # Step 4: Use ffmpeg to create a video from frames
    mp4_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp4")
    ffmpeg.input('frames/frame_%d.png', framerate=24).output(mp4_path).run()
    return mp4_path

@app.route('/convert', methods=['POST'])
def convert_lottie_to_mp4():
    data = request.get_json()
    lottie_url = data.get('lottie_url')

    if not lottie_url:
        return jsonify({'error': 'Lottie URL is required'}), 400

    try:
        # Step 1: Render Lottie to images
        frame_paths = render_lottie_to_images(lottie_url)

        # Step 2: Convert images to MP4
        mp4_path = convert_images_to_mp4(frame_paths)

        # Return the URL to access the MP4 file
        return jsonify({'mp4_url': request.host_url + 'rendered_videos/' + os.path.basename(mp4_path)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
