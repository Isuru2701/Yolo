from flask import Flask, send_from_directory, request, jsonify, redirect
from firebaseConfig.firebaseConfig import db
from service import *
from flask_cors import CORS
import stripe
import os
from dotenv import load_dotenv
import json

from firebaseConfig.FirebaseDriver import FirebaseDriver

app = Flask(__name__)

CORS(app)

load_dotenv() # loads env variables from project's root

stripe.api_key = os.getenv("STRIPE_API_KEY")

YOUR_DOMAIN = 'http://localhost:4242' # Change later

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

    try:
        prices = stripe.Price.list(
            lookup_keys=[request.form['lookup_key']],
            expand=['data.product']
        )

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
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@app.route('/create-portal-session', methods=['POST'])
def customer_portal():
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically this is stored alongside the authenticated user in your database.
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



if __name__ == '__main__':
    app.run(debug=True)
