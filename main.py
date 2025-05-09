import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_lottie_to_mp4():
    data = request.get_json()
    lottie_url = data.get('lottie_url')

    if not lottie_url:
        return jsonify({'error': 'Lottie URL is required'}), 400

    try:
        # Send request to Node.js Puppeteer service
        puppeteer_url = "https://lottie-puppeteer.onrender.com/render"
        response = requests.post(puppeteer_url, json={'lottie_url': lottie_url})
        
        if response.status_code != 200:
            return jsonify({'error': 'Puppeteer failed', 'details': response.text}), 500
        
        mp4_url = response.json().get('mp4_url')
        return jsonify({'mp4_url': mp4_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
