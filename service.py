from firebaseConfig.firebaseConfig import db
import requests
from genres import GENRE_DATA

def create_user(user_data):
    """
    Create a new user in Firestore.

    Parameters:
    - user_data: Dictionary containing user data.

    Returns:
    - Dictionary {"success": bool, "message": str, "user_id": str}
    """
    try:
        # Add the user to Firestore
        user_ref = db.collection('users').add(user_data)

        return {"success": True, "message": "User created successfully", "user_id": user_ref[1].id}
    except Exception as e:
        return {"success": False, "message": str(e), "user_id": None}

def login_user(login_data):
    """
    Login a user by checking email and password in Firestore.

    Parameters:
    - login_data: Dictionary containing email and password.

    Returns:
    - Dictionary {"success": bool, "message": str, "user": dict}
    """
    try:
        # Query Firestore for the user with provided email and password
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', login_data['email']).where('password', '==', login_data['password']).limit(1).get()

        if not query:
            return {"success": False, "message": "Invalid email or password", "user": None}

        user = query[0].to_dict()

        return {"success": True, "message": "Login successful", "user": user}
    except Exception as e:
        return {"success": False, "message": str(e), "user": None}

def media_from_keywords(keywords, media_type):
    url = "https://api.themoviedb.org/3/discover/" + media_type
    api_key = "7e16229611389f1788334e9c9ee5d934"
    params = {'api_key': api_key, 'with_keywords': ','.join(keywords)}

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            movies_data = response.json()

            if 'results' in movies_data:
                for movie in movies_data['results']:
                    # Check if 'genre_ids' is present in the movie object
                    if 'genre_ids' in movie:
                        # Replace genre IDs with genre names
                        genre_names = []
                        for genre_id in movie['genre_ids']:
                            # Use next to get the first match or None if not found
                            genre = next((g for g in GENRE_DATA if g['id'] == genre_id), None)
                            if genre:
                                genre_names.append(genre['name'])
                        movie['genres'] = genre_names
                        # Remove 'genre_ids' as it's no longer needed
                        del movie['genre_ids']

                    # Check if 'poster_path' is present in the movie object
                    if 'poster_path' in movie:
                        # Construct the complete URL for the poster
                        movie['poster_path'] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"

                # Return the updated list of movie objects
                return movies_data['results']
            else:
                print("Error: 'results' key not found in the response.")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
 
def media_from_title(title, media_type):
    """
    Search for media (movies or TV shows) based on the title.

    Parameters:
    - title: String containing the title to search for.
    - media_type: String specifying the type of media (e.g., "movie" or "tv").

    Returns:
    - List of media objects with updated poster URLs and genre names.
    """
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    api_key = "7e16229611389f1788334e9c9ee5d934"
    params = {'api_key': api_key, 'query': title}

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            media_data = response.json()

            if 'results' in media_data:
                for item in media_data['results']:
                    # Check if 'genre_ids' is present in the media object
                    if 'genre_ids' in item:
                        # Replace genre IDs with genre names
                        genre_names = []
                        for genre_id in item['genre_ids']:
                            # Use next to get the first match or None if not found
                            genre = next((g for g in GENRE_DATA if g['id'] == genre_id), None)
                            if genre:
                                genre_names.append(genre['name'])
                        item['genres'] = genre_names
                        # Remove 'genre_ids' as it's no longer needed
                        del item['genre_ids']

                    # Check if 'poster_path' is present in the media object
                    if 'poster_path' in item:
                        # Construct the complete URL for the poster
                        item['poster_path'] = f"https://image.tmdb.org/t/p/w500{item['poster_path']}"

                # Return the updated list of media objects
                return media_data['results']
            else:
                print("Error: 'results' key not found in the response.")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
