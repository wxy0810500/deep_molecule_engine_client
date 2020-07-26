import json
import os

from .settings import BASE_DIR

RUNTIME_ENV = "prod"
SYS_DEBUG = False
CUSTOM_CONFIG_URL = os.path.join(BASE_DIR, 'configuration')

with open(os.path.join(CUSTOM_CONFIG_URL, f'{RUNTIME_ENV}_server_config.json'), 'r') as f:
    SERVER_CONFIG_DICT: dict = json.load(f)
    CACHE_CONFIG_DICT: dict = SERVER_CONFIG_DICT.get('cache')


PREDICTION_TYPE_LIGAND = "ligand"
PREDICTION_TYPE_STRUCTURE = "structure"
PREDICTION_TYPE_NETWORK = "network"
SERVICE_TYPE_SEARCH = "advancedSearch"
SERVICE_TYPE_PREDICTION = "prediction"
