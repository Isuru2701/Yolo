from flask import Flask, send_from_directory, request, jsonify
from firebaseConfig.firebaseConfig import db
from service import *
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])  # serves UI
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/admin', methods=['POST'])
def create_admin():
    """
    **** example payload ***
    {
    "name": "induwara lakindu",
    "email": "induwaralakindu09@gmail.com",
    "password": "Lakindu123",
    "confirmPassword": "Lakindu123",
    "permission_key": "YOLO_SECURITY_CODE_71862736"
    }
    """
    user_data = request.get_json()
    # Validate email uniqueness before creating the user
    existing_user = db.collection('admin').where('email', '==', user_data.get('email')).get()
    if existing_user:
        return {"success": False, "message": "User with this email already exists", "user_id": None}
    
    if user_data['permission_key'] != "YOLO_SECURITY_CODE_71862736":
        return {"success": False, "message": "Request Rejected Unautharized access detected!", "user_id": None}
    
    if user_data['password'] != user_data['confirmPassword']:
        return {"success": False, "message": "Password mismatch, try again", "user_id": None}


    try:
        # Add the user to Firestore
        user_data['confirmPassword'] = ''
        user_data['password'] = hash_password(user_data['password'])
        user_ref = db.collection('admin').add(user_data)
        return {"success": True, "message": "User created successfully", "user_id": user_ref[1].id}
    except Exception as e:
        return {"success": False, "message": str(e), "user_id": None}

@app.route('/admin/login', methods=['POST'])
def admin_login():
    login_data = request.get_json()
    try:
        # Query Firestore for the user with provided email and password
        users_ref = db.collection('admin')
        query = users_ref.where('email', '==', login_data['email']).limit(1).get()

        if not query:
            return {"success": False, "message": "Invalid email or password", "user": None}

        user = query[0].to_dict()
        user['confirmPassword'] = '' 
        print(user['password'])
        # Verify the password using bcrypt
        if not verify_password(login_data['password'], user['password']):
            return {"success": False, "message": "Invalid email or password", "user": None}
        
        return {"success": True, "message": "Login successful", "user": user['name']}
    except Exception as e:
        return {"success": False, "message": str(e), "user": None}


@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    # Validate email uniqueness before creating the user
    existing_user = db.collection('users').where('email', '==', user_data.get('email')).get()
    if existing_user:
        return {"success": False, "message": "User with this email already exists", "user_id": None}

    try:
        user_data['confirmPassword'] = ''
        # Add the user to Firestore
        user_data['password'] = hash_password(user_data['password'])
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
        query = users_ref.where('email', '==', login_data['email']).limit(1).get()

        if not query:
            return {"success": False, "message": "Invalid email or password", "user": None}

        user = query[0].to_dict() 
        print(user['password'])
        # Verify the password using bcrypt
        if not verify_password(login_data['password'], user['password']):
            return {"success": False, "message": "Invalid email or password", "user": None}
        
        return {"success": True, "message": "Login successful", "user": user['name']}
    except Exception as e:
        return {"success": False, "message": str(e), "user": None}

@app.route('/keywords', methods=['GET']) #post : http://localhost:5000/       [prompt : userprompt] as json
def  get_keywords():
    return get_my_keys(request.args.get('prompt'))

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
