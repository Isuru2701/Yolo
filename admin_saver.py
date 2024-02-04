import bcrypt
from firebaseConfig.firebaseConfig import db
from service import hash_password

def create_admin(name, email, password):
    existing_users = db.collection('admin').where('email', '==', email).limit(1).get()

    print("lands here1")
    if existing_users:
        print("lands here")
        return {"success": False, "message": "User with this email already exists", "user_id": None}

    # Add the user to Firestore
    hashed_password = hash_password(password)
    admin_data = {
        "name": name,
        "email": email,
        "password": hashed_password.decode('utf-8')  # Convert bytes to string
    }
    user_ref = db1.collection('admin').add(admin_data)
    return {"success": True, "message": "User created successfully", "user_id": user_ref.id}


# Prompt the user for input
name = input("Enter admin Name: ")
email = input("Enter admin Email: ")
password = input("Enter admin Password: ")

# Create the admin
result = create_admin(name, email, password)
print(result)
