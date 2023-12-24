from flask import Flask, send_from_directory, request, jsonify
from firebaseConfig.firebaseConfig import db

app = Flask(__name__)

@app.route('/')  # serves UI
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/user', methods=['POST'])  # creates a user in Firestore
def create_user():
    try:
        user_data = request.get_json()

        # Add the user to Firestore
        user_ref = db.collection('users').add(user_data)

        return jsonify({"message": "User created successfully", "user_id": user_ref[1].id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
