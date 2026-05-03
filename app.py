from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import asyncio
import os

app = Flask(__name__)
CORS(app)

@app.route('/run-views', methods=['POST'])
def run_views():
    data = request.json
    video_url = data.get('url')
    num_views = data.get('views')

    if not video_url or not isinstance(num_views, int) or num_views <= 0:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        # Call the RunViews.py script with the provided parameters
        command = f'python3 RunViews.py "{video_url}" {num_views}'
        subprocess.Popen(command, shell=True)
        return jsonify({'message': 'Views are being processed'}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)