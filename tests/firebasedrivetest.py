import unittest
from firebaseConfig.FirebaseDriver import FirebaseDriver


class FireBaseTest(unittest.TestCase):

    def setUp(self):
        self.__driver = FirebaseDriver()

    def test_create(self):
        ref = self.__driver.create_document("test","test", {"payload": 0, "a": 1, "b": "c"})
        print(ref)
        self.assertIsNotNone(ref)

    def test_read(self):
        j = self.__driver.read_document("test", "test")
        print(j)
        self.assertIsNotNone(j)

    def test_update(self):
        ref = self.__driver.update_document('test', "test", {"b": self.__driver.FIRESTORE.DELETE_FIELD})
        self.assertIsNotNone(ref)

    def test_delete_document(self):
        self.__driver.delete_document("test", "test")
        j = self.__driver.read_document("test", "test")
        print(j)
        self.assertIsNone(j)


if __name__ == "__main__":
    unittest.main()
