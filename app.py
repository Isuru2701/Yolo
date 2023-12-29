from flask import Flask, send_from_directory, request, jsonify
from firebaseConfig.firebaseConfig import db
from service import *

app = Flask(__name__)

@app.route('/')  # serves UI
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    return jsonify(create_user(user_data))
      
    

@app.route('/users/login', methods=['POST'])
def login():
    login_data = request.get_json()
    return jsonify(login_user(login_data))

@app.route('/movies')
def get_movies():
    keywords = ['fighting', 'adventures', 'romantic']
    return jsonify(media_from_keywords(keywords, "movie"))
      
@app.route('/api/media', methods=['GET'])
def get_media():
    # Get parameters from the query string
    title = request.args.get('title', default='', type=str)
    media_type = request.args.get('media_type', default='', type=str)

    if not title or not media_type:
        return jsonify({"error": "Both 'title' and 'media_type' parameters are required."}), 400

    if media_type == "movie" or media_type == "tv":
        result = media_from_title(title=title, media_type=media_type)
    elif media_type == "song":
        return "spotify API under development"   
    elif media_type == "book":
        return "book fetching api under development"

    if result is not None:
        return jsonify(result)
    else:
        return jsonify({"error": "An error occurred while fetching media data."}), 500


if __name__ == '__main__':
    app.run(debug=True)
