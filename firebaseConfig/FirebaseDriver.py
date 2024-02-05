import os
import secrets
import json
import firebase_admin
from firebase_admin import credentials, firestore, db, exceptions
from dotenv import load_dotenv


class FirebaseDriver:
    """Contains generic code that allows for CRUD operations with Firebase Firestore"""

    # TODO: rn this is redundant with firebaseConfig.py, fix and refactor later

    def __init__(self):

        # read firebase config key
        load_dotenv()
        try:
            cert_str = os.getenv("FIREBASE_CONFIG")
            print(cert_str)

            if cert_str:  # Null check
                cert = json.loads(cert_str)

                cred = credentials.Certificate(cert)  # form credentials from

                try:
                    app = firebase_admin.initialize_app(cred, {
                        "databaseURL": cert.get("databaseURL", "https://yolo-bbea6.firebaseio.com")
                    })

                    self.__db = firestore.client()
                except ValueError:
                    raise ValueError("Value Error at Firebase Driver .__init__")

            else:
                print("FIREBASE_CONFIG environment variable not set")

            self.FIRESTORE = firestore.firestore  # used to manage special builtin-values

        except IOError:
            print(".env config file cannot be found")

    def create_document(self, collection: str, document:str, json=None):
        """
        Creates a document in the provided collection with the provided json (default=None)

        :param collection: collection name
        :param document: document name
        :param json: json payload
        :return:
        """

        ref = self.__db.collection(collection).document(document).set(json)
        return ref

    def read_document(self, collection: str, document: str):
        """
        Fetches the contents of a document
        :param collection:
        :param document:
        :return:
        """
        ref = self.__db.collection(collection).document(document)
        doc = ref.get()
        print(doc.to_dict())
        if doc:
            return doc.to_dict()
        else:
            return None

    def update_document(self, collection: str, document: str, json):
        """
        Updates a document with the provided json
        :param collection:
        :param document:
        :param json:
        :return:
        """
        ref = self.__db.collection(collection).document(document)
        ref.update(json)
        return ref.id

    def delete_document(self, collection: str, document: str):
        """
        deletes the document and any sub-collections inside
        :param collection:
        :param document:
        :return:
        """
        ref = self.__db.collection(collection).document(document)
        ref.delete()
