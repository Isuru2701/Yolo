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

@app.route('/keywords', methods=['POST']) #post : http://localhost:5000/       [prompt : userprompt] as json
def  get_keywords():
    return get_my_keys(request.args.post('prompt'))

@app.route('/movies', methods=['GET']) #example request : http://localhost:5000/movies?keywords=marvel,adventure&media_type=movie (movie / tv)
def get_movies():
    keywords_param = request.args.get('keywords')
    keywords = keywords_param.split(',') if keywords_param else []
    media_type = request.args.get('media_type')
    return jsonify(media_from_keywords(keywords, media_type))

@app.route('/songs', methods=['GET']) #example request : http://localhost:5000/songs?keywords=marvel,adventure&media_type=song (song / video)
def get_audio():
    keywords_string = request.args.get('keywords', default='', type=str)
    media_type = request.args.get('media_type', default='', type=str)
    keywords_array = keywords_string.split(',')
    result = get_songs(keywords_array, media_type)
    return jsonify(result)

@app.route('/books', methods=['GET']) #example request : http://localhost:5000/books?keywords=marvel,adventure
def get_reads():
    keywords_string = request.args.get('keywords', default='', type=str)
    keywords_array = keywords_string.split(',')
    return jsonify(get_books(keywords_array))
      
@app.route('/anime', methods=['GET']) #example request : http://localhost:5000/anime?keywords=marvel,adventure&media_type=movie (movie / tv)
def get_animes():
    keywords_string = request.args.get('keywords', default='', type=str)
    media_type = request.args.get('media_type', default='', type=str)
    keywords_array = keywords_string.split(',')
    return get_anime(keywords_array, media_type)


#public endpoint need a dynamic api key assiging and validation for developer role unlocked users
@app.route('/api/media', methods=['GET']) #example request : http://localhost:5000/api/media?title=TITLE_OF_THE_CONTENT&media_type=MEDIA (movie,tv, anime_movie, anime_tv, song, book)
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
    elif media_type == "anime_movie":
        return jsonify(get_anime([title], 'movie'))
    elif media_type == "anime_tv":
        return jsonify(get_anime([title], 'tv'))
    else:
        return jsonify({"error": "Media_type invalid"}), 400
    

    if result is not None:
        return jsonify(result)
    else:
        return jsonify({"error": "An error occurred while fetching media data."}), 500

if __name__ == '__main__':
    app.run(debug=True)
