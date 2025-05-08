from flask import Flask, request, jsonify
import os
import requests
import uuid
from py_lottie import load
from PIL import Image
import ffmpeg

app = Flask(__name__)

OUTPUT_DIR = "./rendered_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def render_lottie_to_images(lottie_url):
    # Fetch the Lottie JSON file
    response = requests.get(lottie_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch Lottie JSON.")
    
    # Load the Lottie animation
    lottie_data = load(response.json())

    # Render frames from the animation
    frame_paths = []
    num_frames = 60  # Adjust as needed for frame count or duration

    for frame in range(num_frames):
        # Render the frame (just an example, adjust this for actual frame rendering)
        frame_image = lottie_data.render_frame(frame / num_frames)  # Adjust frame based on time or position
        image_path = os.path.join(OUTPUT_DIR, f"frame_{frame}.png")
        frame_paths.append(image_path)
        frame_image.save(image_path)
    
    return frame_paths

def convert_images_to_mp4(frame_paths):
    # Use ffmpeg to convert image sequence to MP4
    mp4_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp4")
    ffmpeg.input('frame_%d.png', framerate=24).output(mp4_path).run()
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
