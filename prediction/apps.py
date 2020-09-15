from django.apps import AppConfig
from .taskManager import initProcessPool
from .predictionTask import processOneTask
import os


class PredictionConfig(AppConfig):
    name = 'prediction'

    def ready(self):
        cmd = os.environ.get('RUNTIME_COMMAND')
        if cmd and cmd == 'runserver':
            initProcessPool(processOneTask)


