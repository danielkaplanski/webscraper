from flask import Flask, request, jsonify
from pymongo import MongoClient
import multiprocessing
import json
from bson import ObjectId
from scraper import run_async_scraper

app = Flask(__name__)

# Inicjalizacja MongoDB
client = MongoClient('mongo', 27017)
db = client.scraping_db
collection = db.scraped_data
profile_collection = db.profiles

# Klasa do konwersji ObjectId na string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

app.json_encoder = JSONEncoder

@app.route('/set_profile', methods=['POST'])
def set_profile():
    profile = request.json.get('profile')
    profile_name = request.json.get('profile_name')
    if not profile or not profile_name:
        return jsonify({"error": "Profile or profile name not provided"}), 400

    profile_collection.replace_one({'profile_name': profile_name}, {'profile_name': profile_name, 'profile': profile}, upsert=True)
    return jsonify({"status": "Profile set", "profile_name": profile_name})

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    urls = request.json.get('urls')
    profile_name = request.json.get('profile_name')
    if not urls or not profile_name:
        return jsonify({"error": "No URLs or profile name provided"}), 400

    profile_doc = profile_collection.find_one({'profile_name': profile_name})
    if not profile_doc:
        return jsonify({"error": "Profile not found"}), 400

    profile = profile_doc['profile']
    pool = multiprocessing.Pool()
    results = pool.starmap(run_async_scraper, [(urls, profile)])
    pool.close()
    pool.join()

    # Zapisz dane z ostatniego scrapowania w bazie danych
    for result_set in results:
        for result, _ in result_set:
            if result:
                collection.insert_one(result)

    return jsonify({"status": "Scraping started"})

@app.route('/get_data', methods=['GET'])
def get_data():
    # Pobierz dane z ostatniego scrapowania
    last_data = collection.find().sort('_id', -1).limit(1)
    data = []
    for doc in last_data:
        doc['_id'] = str(doc['_id'])
        data.append(doc)
    return jsonify(data)

@app.route('/get_history', methods=['GET'])
def get_history():
    # Pobierz historię URLi
    urls = collection.distinct('url')
    return jsonify(urls)

@app.route('/get_data_by_url', methods=['POST'])
def get_data_by_url():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    data = list(collection.find({"url": url}, {'_id': 0}))
    return jsonify(data)

@app.route('/delete_data_by_url', methods=['POST'])
def delete_data_by_url():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    result = collection.delete_many({"url": url})
    return jsonify({"status": "Deleted", "deleted_count": result.deleted_count})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
