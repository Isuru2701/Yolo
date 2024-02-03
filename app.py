from flask import Flask, send_from_directory, request, jsonify
from firebaseConfig.firebaseConfig import db
from service import *
from flask_cors import CORS

app = Flask(__name__)

CORS(app)


@app.route('/')  # serves UI
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()

    # Validate email uniqueness before creating the user
    existing_user = db.collection('users').where('email', '==', user_data.get('email')).get()
    if existing_user:
        return {"success": False, "message": "User with this email already exists", "user_id": None}

    try:
        # Add the user to Firestore
        user_ref = db.collection('users').add(user_data)

        return {"success": True, "message": "User created successfully", "user_id": user_ref[1].id}
    except Exception as e:
        return {"success": False, "message": str(e), "user_id": None}


@app.route('/users/login', methods=['POST'])
def login():
    login_data = request.get_json()
    try:
        # Query Firestore for the user with provided email and password
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', login_data['email']).where('password', '==',
                                                                          login_data['password']).limit(1).get()

        if not query:
            return {"success": False, "message": "Invalid email or password", "user": None}

        user = query[0].to_dict()

        return {"success": True, "message": "Login successful", "user": user}
    except Exception as e:
        return {"success": False, "message": str(e), "user": None}


@app.route('/keywords', methods=['GET'])  # post : http://localhost:5000/       [prompt : userprompt] as json
def get_keywords():
    return get_my_keys(request.args.get('prompt'))


@app.route('/movies', methods=[
    'GET'])  # example request : http://localhost:5000/movies?keywords=marvel,adventure&media_type=movie (movie / tv)
def get_movies():
    keywords_param = request.args.get('keywords')
    keywords = keywords_param.split(',') if keywords_param else []
    media_type = request.args.get('media_type')
    return jsonify(media_from_keywords(keywords, media_type))


@app.route('/songs', methods=[
    'GET'])  # example request : http://localhost:5000/songs?keywords=marvel,adventure&media_type=song (song / video)
def get_audio():
    keywords_string = request.args.get('keywords', default='', type=str)
    media_type = request.args.get('media_type', default='', type=str)
    keywords_array = keywords_string.split(',')
    result = get_songs(keywords_array, media_type)
    return jsonify(result)


@app.route('/books', methods=['GET'])  # example request : http://localhost:5000/books?keywords=marvel,adventure
def get_reads():
    keywords_string = request.args.get('keywords', default='', type=str)
    keywords_array = keywords_string.split(',')
    return jsonify(get_books(keywords_array))


@app.route('/anime', methods=[
    'GET'])  # example request : http://localhost:5000/anime?keywords=marvel,adventure&media_type=movie (movie / tv)
def get_animes():
    keywords_string = request.args.get('keywords', default='', type=str)
    media_type = request.args.get('media_type', default='', type=str)
    keywords_array = keywords_string.split(',')
    return get_anime(keywords_array, media_type)


# public endpoint need a dynamic api key assiging and validation for developer role unlocked users
@app.route('/api/media', methods=[
    'GET'])  # example request : http://localhost:5000/api/media?title=TITLE_OF_THE_CONTENT&media_type=MEDIA (movie,tv, anime_movie, anime_tv, song, book)
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


# developer API endpoint
@app.route('/developers')
def fetchInfo(name: str):
    # TODO: if it's been a month, reset the quota
    # Note: All tokens share the same quota
    pass


@app.route('developers/generate')
def generateToken():
    pass


@app.route('developers/invalidate')
def invalidateToken():
    pass


if __name__ == '__main__':
    app.run(debug=True)
