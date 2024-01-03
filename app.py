from flask import Flask, send_from_directory, request, jsonify
from firebaseConfig.firebaseConfig import db
from service import *

app = Flask(__name__)

@app.route('/')  # serves UI
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/users', methods=['POST']) #
def create_user():
    user_data = request.get_json()
    return jsonify(create_user(user_data))

@app.route('/users/login', methods=['POST'])
def login():
    login_data = request.get_json()
    return jsonify(login_user(login_data))

@app.route('/movies') #example request : http://localhost:5000/movies?keywords=marvel,adventure&media_type=movie
def get_movies():
    keywords_param = request.args.get('keywords')
    keywords = keywords_param.split(',') if keywords_param else []
    media_type = request.args.get('media_type')
    return jsonify(media_from_keywords(keywords, media_type))
    
@app.route('/keywords', methods=['POST']) #post : http://localhost:5000/       [prompt : userprompt] as json
def  get_keywords():
    return get_my_keys(request.args.post('prompt'))

@app.route('/songs') #example request : http://localhost:5000/songs?keywords=marvel,adventure&media_type=song (song / video)
def get_audio():
    keywords_string = request.args.get('keywords', default='', type=str)
    media_type = request.args.get('media_type', default='', type=str)
    keywords_array = keywords_string.split(',')
    result = get_songs(keywords_array, media_type)
    return jsonify(result)

@app.route('/books') #example request : http://localhost:5000/books?keywords=marvel,adventure
def get_reads():
    keywords_string = request.args.get('keywords', default='', type=str)
    keywords_array = keywords_string.split(',')
    return jsonify(get_books(keywords_array))

      
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
        return jsonify(get_songs([title], media_type))   
    elif media_type == "book":
        return jsonify(get_books([title]))

    if result is not None:
        return jsonify(result)
    else:
        return jsonify({"error": "An error occurred while fetching media data."}), 500

if __name__ == '__main__':
    app.run(debug=True)
