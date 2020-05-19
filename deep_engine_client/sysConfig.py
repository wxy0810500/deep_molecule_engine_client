import json
import os

from .settings import BASE_DIR

CUSTOM_CONFIG_URL = os.path.join(BASE_DIR, 'configuration')

with open(os.path.join(CUSTOM_CONFIG_URL, 'server_config.json'), 'r') as f:
    # f = open(os.path.join(CUSTOM_CONFIG_URL, '209server_config.json'), 'r')
    SERVER_CONFIG_DICT: dict = json.load(f)
    CACHE_CONFIG_DICT: dict = SERVER_CONFIG_DICT.get('cache')


PREDICTION_TYPE_LIGAND = "ligand"
PREDICTION_TYPE_STRUCTURE = "structure"
SERVICE_TYPE_SEARCH = "search"
SERVICE_TYPE_PREDICTION = "prediction"
