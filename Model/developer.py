from genericuser import GenericUser


class Developer(GenericUser):
    """
    Class for handling all aspects of a developer
    each developer has a quota, a used amount, and one or more access tokens
    """

    def __init__(self):
        super().__init__()
        self.__quota: int = 10000
        self.__usage: int = 0
        self.__accessTokens: list = []  # List of valid strings

    def generateToken(self):
        pass

    def invalidateToken(self):
        pass

    def fetch(self):
        pass
        # TODO: get info from firebase here
