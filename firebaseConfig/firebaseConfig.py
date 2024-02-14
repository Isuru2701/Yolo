import os
import secrets
import json
import firebase_admin
from firebase_admin import credentials, firestore, db

try:

    cert_str = os.getenv("FIREBASE_CONFIG")  # Read Firebase config from environment variable

    if cert_str:
        cert = json.loads(cert_str)
        cred = credentials.Certificate(cert)

        try:
            app = firebase_admin.initialize_app(cred, {
                "databaseURL": cert.get("databaseURL", "https://yolo-bbea6.firebaseio.com")  
            })
            
            db = firestore.client()# Get Firestore database instance

            # __________Now 'db' can be used for Firestore operations___________

        except ValueError:
            print("VALUE_ERROR: Database .__init__ app instance already exists or something else went wrong")

    else:
        print("FIREBASE_CONFIG environment variable not set")

except IOError:
    print("IOError: Database .__init__ Config file not found")
