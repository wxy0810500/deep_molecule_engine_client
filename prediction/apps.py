from django.apps import AppConfig
from .taskManager import initProcessPool
from .predictionTask import processOneTask


class PredictionConfig(AppConfig):
    name = 'prediction'

    def ready(self):
        initProcessPool(processOneTask)
