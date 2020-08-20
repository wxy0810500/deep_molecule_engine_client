from django.shortcuts import render


class CommonException(Exception):

    def __init__(self, message):
        super.__init__(message)
        self.message = message


class PredictionCommonException(CommonException):

    def __init__(self, message):
        super.__init__(message)
        self.message = message


def return400ErrorPage(request, form):
    return render(request, "400.html", {'errorForm': form})
