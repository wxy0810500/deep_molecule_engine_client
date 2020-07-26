from django.conf import settings


def printDebug(self, *args, sep=' ', end='\n', file=None):
    if settings.DEBUG:
        print(self, *args, sep=sep, end=end, file=file)
