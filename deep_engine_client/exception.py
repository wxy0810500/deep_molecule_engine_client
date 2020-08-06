class CommonException(Exception):

    def __init__(self, message):
        super.__init__(message)
        self.message = message


class PredictionCommonException(CommonException):

    def __init__(self, message):
        super.__init__(message)
        self.message = message
