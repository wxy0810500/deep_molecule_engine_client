import json
import os

from .settings import BASE_DIR

CUSTOM_CONFIG_URL = os.path.join(BASE_DIR, 'configuration')

f = open(os.path.join(CUSTOM_CONFIG_URL, 'server_config.json'), 'r')
SERVER_CONFIG_DICT: dict = json.load(f)
f.close()
