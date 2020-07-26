
class PredictionCommonException(Exception):

    def __init__(self, message):
        super.__init__(message)
        self.message = message


class CommonException(Exception):

    def __init__(self, message):
        super.__init__(message)
        self.message = message
