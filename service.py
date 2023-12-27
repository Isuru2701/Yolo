from firebaseConfig.firebaseConfig import db

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
