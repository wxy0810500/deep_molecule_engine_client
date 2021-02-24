from django.apps import AppConfig
from prediction.taskManager import initProcessPool
from prediction.predictionTask import processOneTask
import os


class InfectiousDiseaseConfig(AppConfig):
    name = 'infectiousDisease'

    def ready(self):
        cmd = os.environ.get('RUNTIME_COMMAND')
        if cmd and cmd == 'runserver':
            initProcessPool(processOneTask)


