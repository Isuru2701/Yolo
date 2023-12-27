from flask import Flask, send_from_directory, request, jsonify
from firebaseConfig.firebaseConfig import db
from service import create_user, login_user

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

      

if __name__ == '__main__':
    app.run(debug=True)
