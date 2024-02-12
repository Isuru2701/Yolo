from flask import Flask, send_from_directory, request, jsonify, redirect
from service import *
from flask_cors import CORS
import stripe
import os
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime
from firebaseConfig.FirebaseDriver import FirebaseDriver
from twilio.rest import Client
import random

app = Flask(__name__)

CORS(app)

load_dotenv()  # loads env variables from project's root

stripe.api_key = os.getenv("STRIPE_API_KEY")

YOUR_DOMAIN = 'http://localhost:5000'  # Change later


# Endpoint to send OTP
@app.route('/otp/send', methods=['POST'])
def send_otp():
    try:
        # Get phone number from request data
        phone = request.json['phone']
        
        # Generate a random 6-digit OTP
        otp = ''.join(random.choices('0123456789', k=6))

        # Store phone number and OTP in Firestore
        db.collection('creator_validation_otps').document(phone).set({
            'otp': otp
        })

        # Replace this with your actual function to send the OTP via SMS
        if send_message(otp, phone) == True:
            return jsonify({'success': True, 'message': 'OTP sent successfully'})
        return jsonify({'success': False, 'message': "otp not sent"})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Endpoint to check OTP
@app.route('/otp/check', methods=['POST'])
def check_otp():
    try:
        # Get phone number and user-entered OTP from request data
        phone = request.json['phone']
        user_entered_otp = request.json['otp']

        # Retrieve stored OTP from Firestore
        stored_otp_doc = db.collection('creator_validation_otps').document(phone).get()
        if stored_otp_doc.exists:
            stored_otp = stored_otp_doc.to_dict()['otp']
            
            # Check if user-entered OTP matches stored OTP
            if str(user_entered_otp) == stored_otp:
                return jsonify({'success': True, 'message': 'OTP validated successfully'})
            else:
                return jsonify({'success': False, 'message': 'Invalid OTP'})
        else:
            return jsonify({'success': False, 'message': 'No OTP found for the provided phone number'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
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
        user_data['role'] = 'user'
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
        # Verify the password using bcrypt
        if not verify_password(login_data['password'], user['password']):
            return {"success": False, "message": "Invalid email or password", "user": None}
        key = user['password'].decode('utf-8')
        return {"success": True, "message": "Login successful", "user": user['name'],"email" : user['email'], "role": user['role'], "password" : key}
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


@app.route('/anime', methods=['GET'])  # example request : http://localhost:5000/anime?keywords=marvel,adventure&media_type=movie (movie / tv)
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


@app.route('/developers/generate', methods=['POST'])
def generateToken():
    pass


@app.route('/developers/invalidate', methods=['POST'])
def invalidateToken():
    pass


# developer related API endpoints
@app.route('/developers', methods=['POST'])
def fetch_dev_info(name: str):
    # TODO: if it's been a month, reset the quota
    # Note: All tokens share the same quota
    pass


@app.route('/developers/generate', methods=['GET'])
def generateApiToken():
    pass


@app.route('/developers/invalidate', methods=['GET'])
def invalidateApiToken():
    pass


@app.route('/api/', methods=['POST'])
def processRequest():
    """
    every api call must have the following:

    :return:
    """
    pass

# Content creators

@app.route('/creator', methods=['POST'])
def updateCreatorRole():
    """
    Update the user's role to content creator based on the provided user ID and password hash,
    or check the user's role.
    payload{
      "userEmail": "",
      "userContactNumber": "",
      "status":"check/set"
    }
    """
    user_data = request.get_json()
    users_ref = db.collection('users')
    if user_data['status'] == "check":
        query = users_ref.where('email', '==', user_data['userEmail']).limit(1).get()
        user_docs = list(query)
        if len(user_docs) == 1:
            user = user_docs[0]
            user_role = user.get('role')
            if user_role == 'creator':
                return {"success": True, "message": "Creator"}
            elif user_role == 'user':
                return {"success": True, "message": "User"}
            else:
                return {"success": False, "message": "Role not defined"}
        else:
            return {"success": False, "message": "User does not exist"}
    elif user_data['status'] == "set":
        required_fields = ['userEmail', 'userPasswordHash', 'userContactNumber']
        if not all(field in user_data for field in required_fields):
            return {"success": False, "message": "Missing required fields"}
        query = users_ref.where('email', '==', user_data['userEmail']).limit(1).get()
        user_docs = list(query)
        if len(user_docs) == 1:
            if approve_user(user_data['userPasswordHash'], user_data['userEmail']):
                user_docs[0].reference.set({
                    'role': 'creator',
                    'contactNumber': user_data['userContactNumber']
                }, merge=True)
                return {"success": True, "message": "User role updated to creator"}
            else:
                return {"success": False, "message": "Unauthorized access"}
        else:
            return {"success": False, "message": "User does not exist. Please log in again"}


# check all boost requests
@app.route('/creator/requests/', methods=['GET'])
def fetch_all_requests():
    contents = []

    # Query all collections
    contents_ref = db.collection('content').stream()
    for doc in contents_ref:
        contents_data = doc.to_dict()
        contents.append(contents_data)

    return jsonify(contents), 200


#accept or reject boost request
@app.route('/creator/requests/validate', methods=['POST'])
def validate_requests():
    """
    payload{
        "request_id": "",
        "admin": "admin_id",
        "hash": "admin_password_hash",
        "status": "true/false"
    }
    :return:
    """

    #check if admin


    data = request.get_json()
    r_id = data.get('request_id')
    approval = data.get('status') #boolean True or False

    contents_ref = db.collection('content').document(r_id)
    contents_ref.update({
        'status': 'approved' if approval else 'rejected'
    })

    return jsonify({'message': 'Request updated successfully'}), 200







#register for premium
@app.route('/user/premium/record', methods=['POST'])
def register_for_premium():
    pass


@app.route('/content', methods=['POST'])
def saveContent():
    """Store content in the content table with status pending,
    which can be changed by the admin from their UI. If approved,
    the status should be changed to approved. Only approved collections
    should be displayed in the UI.

    Payload:
    {
        "content_type": "movie",
        "content_url": "http://example.com",
        "keywords": ["keyword1", "keyword2"]
    }
    """
    try:
        content_data = request.get_json()
        content_data['status'] = "pending"
        
        # Save content data to Firestore collection
        doc_ref = db.collection('content').document()
        doc_ref.set(content_data)

        return {"success": True, "message": "Data saved successfully"}, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route('/admin/content/approve', methods=['post'])
def updateContentStatus():
    """to approve he should verify if he is a admin or not
    so in the payload we fetch hash and validate him b4 approving content
        {

        }
    """
    content_data = request.get_json()
    #check the role as admin?
    
    #update the content 
    content_data['status'] = "approved"
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    content_data['date'] = formatted_datetime


# PAYMENT GATEWAY
@app.route('/payment/', methods=['POST'])
def make_payment():
    details = request.get_json()


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    request must have:
    - lookup_key

    :return:
    """
    payment_data = request.get_json()
    print(payment_data['lookup_key'])

    print(stripe.api_key)
    prices = stripe.Price.list(
            lookup_keys=[payment_data['lookup_key']],
            expand=['data.product']
        )
    print(prices)
    
    try:
        

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html'
            ,
        )
        return {"success": True, "url": checkout_session.url}
    except Exception as e:
        print(e)
        return "Server error", 500


@app.route('/create-portal-session', methods=['POST'])
def customer_portal():
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically, this is stored alongside the authenticated user in your database.
    checkout_session_id = request.form.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = YOUR_DOMAIN

    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)


@app.route('/webhook', methods=['POST'])
def webhook_received():
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        print('Subscription canceled: %s', event.id)

    return jsonify({'status': 'success'})


# Collections endpoints

@app.route('/collections/', methods=['GET'])
def fetch_collections():
    collections = []

    # Query all collections
    collection_ref = db.collection('collections').stream()
    for doc in collection_ref:
        collection_data = doc.to_dict()
        collections.append(collection_data)

    return jsonify(collections), 200


@app.route('/collections/search ', methods=["GET"])
def search_collections():
    """
    /collections/search?keys=key_1,key_2,key_3....key_n
    """
    keys = request.args.get('keys')
    print(keys)
    if keys:
        key_list = keys.split(',')
    else:
        return jsonify({'error': "EMPTY_KEYS"}), 400




@app.route('/collections/', methods=['POST'])
def create_collection():
    """

    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    # Extracting fields from the JSON
    title = data.get('title')
    description = data.get('description')
    keywords = data.get('keywords')
    contents = list(data.get('contents'))
    duration = data.get('duration')
    premium = data.get('premium')

    # Generate a unique ID
    unique_id = str(uuid.uuid4())

    # Write data to Firestore
    collection_ref = db.collection('collections').document(unique_id)
    collection_ref.set({
        'title': title,
        'description': description,
        'keywords': keywords.split(','),
        'contents': contents,
        'duration': duration,
        'premium': premium
    })

    return jsonify({'message': 'Collection created successfully', 'collection_id': unique_id}), 201


@app.route('/collections/<collection_id>', methods=['DELETE'])
def delete_collections(collection_id):
    # Check if the collection exists
    collection_ref = db.collection('collections').document(collection_id)
    if not collection_ref.get().exists:
        return jsonify({'error': 'Collection not found'}), 404

    # Delete the collection
    collection_ref.delete()

    return jsonify({'message': 'Collection deleted successfully'}), 200


@app.route('/collections/', methods=["PUT"])
def edit_collections():
    pass


@app.route('/collections/', methods=['POST'])
def assign_collections():
    pass


if __name__ == '__main__':
    app.run(debug=True)
