import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_profile', methods=['POST'])
def set_profile():
    profile = request.json.get('profile')
    profile_name = request.json.get('profile_name')
    if not profile or not profile_name:
        return jsonify({"error": "Profile or profile name not provided"}), 400

    response = requests.post('http://backend:5001/set_profile', json={'profile_name': profile_name, 'profile': profile})
    return response.json()

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    urls = request.json.get('urls')
    profile_name = request.json.get('profile_name')
    if not urls or not profile_name:
        return jsonify({"error": "No URLs or profile name provided"}), 400

    response = requests.post('http://backend:5001/start_scraping', json={'urls': urls, 'profile_name': profile_name})
    return response.json()

@app.route('/get_data', methods=['GET'])
def get_data():
    response = requests.get('http://backend:5001/get_data')
    return response.json()

@app.route('/get_history', methods=['GET'])
def get_history():
    response = requests.get('http://backend:5001/get_history')
    return response.json()

@app.route('/get_data_by_url', methods=['POST'])
def get_data_by_url():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    response = requests.post('http://backend:5001/get_data_by_url', json={'url': url})
    return response.json()

@app.route('/delete_data_by_url', methods=['POST'])
def delete_data_by_url():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    response = requests.post('http://backend:5001/delete_data_by_url', json={'url': url})
    return response.json()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
