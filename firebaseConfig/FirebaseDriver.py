import os
import secrets
import json
import firebase_admin
from firebase_admin import credentials, firestore, db, exceptions


class FirebaseDriver:
    """Contains generic code that allows for CRUD operations with Firebase Firestore"""

    # TODO: rn this is redundant with firebaseConfig.py, fix and refactor later

    def __init__(self):
        # read firebase config key
        cert_str: str = os.getenv("FIREBASE_CONFIG")

        if cert_str: # Null check
            cert = json.loads(cert_str)
            cred = credentials.Certificate(cert) # form credentials from

            try:
                app = firebase_admin.initialize_app(cred, {
                    "databaseURL": cert.get("databaseURL","https://yolo-bbea6.firebaseio.com")
                })
            except:
                pass



