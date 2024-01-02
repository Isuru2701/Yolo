from firebaseConfig.firebaseConfig import db
import requests
from genres import GENRE_DATA
from engine import keyword_engine
import time
from random import shuffle

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
    keyword_ids = get_keyword_ids(api_key, keywords)
    keywords_str = '|'.join(map(str, keyword_ids))
    params = {
        'api_key': api_key,
        'with_keywords': keywords_str
    }

    #search_from_titles(keywords)

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

def media_from_keywords_and_search(keywords, media_type, title_results=5, keyword_results=10):
    url_search = f"https://api.themoviedb.org/3/search/{media_type}"
    url_discover = f"https://api.themoviedb.org/3/discover/{media_type}"

    api_key = "7e16229611389f1788334e9c9ee5d934"

    # Step 1: title an overview Search
    top_results_from_title = []
    try:
        for keyword in keywords:
            basic_search_params = {'api_key': api_key, 'query': keyword}
            response_search = requests.get(url_search, params=basic_search_params)

            if response_search.status_code == 200:
                basic_search_data = response_search.json()

                if 'results' in basic_search_data:
                    # take the top results from each keyword search
                    for result in basic_search_data['results'][:title_results]:
                        # Check and add missing fields
                        if 'poster_path' not in result:
                            result['poster_path'] = None
                        if 'genre_ids' not in result:
                            result['genre_ids'] = []
                        
                        # replace genre ids with names
                        genre_names = []
                        for genre_id in result['genre_ids']:
                            genre = next((g for g in GENRE_DATA if g['id'] == genre_id), None)
                            if genre:
                                genre_names.append(genre['name'])
                        result['genres'] = genre_names
                        
                        # Remove 'genre_ids' as it's no longer needed
                        del result['genre_ids']

                        # set full path to poster
                        if 'poster_path' in result:
                            result['poster_path'] = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
                        
                        top_results_from_title.append(result)
                else:
                    print(f"Error: 'results' key not found in the basic search response for keyword: {keyword}")
            else:
                print(f"Error in basic search for keyword {keyword}: {response_search.status_code} - {response_search.text}")
                return None
            time.sleep(1)

    except Exception as e:
        print(f"An error occurred during basic search: {e}")
        return None

    # Step 2: keyword search
    keyword_ids = get_keyword_ids(api_key, keywords)
    keywords_str = ','.join(map(str, keyword_ids))

    discover_params = {
        'api_key': api_key,
        'with_keywords': keywords_str
    }

    try:
        response_discover = requests.get(url_discover, params=discover_params)

        if response_discover.status_code == 200:
            discover_data = response_discover.json()

            if 'results' in discover_data:
                for movie in discover_data['results'][:keyword_results]:
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

                # Combine the results from basic search and refined search
                combined_results = top_results_from_title + discover_data['results'][:keyword_results]
                shuffle(combined_results)
                return combined_results
            else:
                print("Error: 'results' key not found in the refined search response.")
                return None
        else:
            print(f"Error in refined search: {response_discover.status_code} - {response_discover.text}")
            return None

    except Exception as e:
        print(f"An error occurred during refined search: {e}")
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
    
def get_my_keys(prompt):
    return keyword_engine(prompt)

def get_keyword_ids(api_key, keyword):
    url = f"https://api.themoviedb.org/3/search/keyword"
    keyword_ids = []

    for word in keyword:
        params = {
            'api_key': api_key,
            'query': word
        }

        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                keyword_data = response.json()
                if 'results' in keyword_data:
                    # Get the top 5 keyword IDs for each word
                    word_ids = [kw['id'] for kw in keyword_data['results'][:5]]
                    keyword_ids.extend(word_ids)
                else:
                    print(f"Error: 'results' key not found in the response for {word}.")
            else:
                print(f"Error: {response.status_code} - {response.text} for {word}")

            time.sleep(1)  # Introduce a 1-second delay between API calls

        except Exception as e:
            print(f"An error occurred for {word}: {e}")

    return keyword_ids






