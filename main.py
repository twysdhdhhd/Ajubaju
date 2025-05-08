from flask import Flask, request, jsonify
import os
import requests
from moviepy.editor import VideoFileClip
import uuid

app = Flask(__name__)

# Temporary storage for rendered files
OUTPUT_DIR = "./rendered_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert_lottie_to_mp4():
    data = request.get_json()
    lottie_url = data.get('lottie_url')

    if not lottie_url:
        return jsonify({'error': 'Lottie URL is required'}), 400

    try:
        # Download Lottie JSON
        response = requests.get(lottie_url)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch Lottie JSON'}), 400

        lottie_json_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.json")
        with open(lottie_json_path, 'w') as json_file:
            json_file.write(response.text)

        # Convert Lottie JSON to MP4 (using moviepy as placeholder, replace with lottie-web renderer)
        mp4_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp4")
        # For now, this is a placeholder. Replace with actual Lottie to MP4 conversion logic
        clip = VideoFileClip("sample.mp4")  # Replace with actual rendering logic
        clip.write_videofile(mp4_path)

        return jsonify({'mp4_url': request.host_url + 'rendered_videos/' + os.path.basename(mp4_path)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
