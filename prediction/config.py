from configuration.sysConfig import SYSTEM_CONFIG_DICT

# prediction_CFG
PREDICTION_CFG_DICT = SYSTEM_CONFIG_DICT.get('prediction')

PREDICTION_SERVER_HOST = PREDICTION_CFG_DICT.get("serverHost")
PREDICTION_SERVER_TIMEOUT = PREDICTION_CFG_DICT.get("timeout")
PREDICTION_SERVER_MODEL_CFG = PREDICTION_CFG_DICT.get("modelCfg")


PREDICTION_TYPE_LIGAND = "ligand"
PREDICTION_TYPE_STRUCTURE = "structure"
PREDICTION_TYPE_NETWORK = "network"