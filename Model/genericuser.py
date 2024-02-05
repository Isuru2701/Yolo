class GenericUser:
    """holds basic functionality shared by across all users"""

    def __init__(self):
        pass


    def register(self, name: str, country:str, email:str, password:str, confirmPassword:str):
        pass


    def login(self, name:str, hasedPassword:str):
        pass


    def makePayment(self, amount: float, recurring: bool):
        pass
        #TODO: authenticate first
        #TODO: connect to payment gateway


    def cancelRecurring(self):
        #TODO: authenticate first
        pass
