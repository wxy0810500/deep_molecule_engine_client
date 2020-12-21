from configuration.sysConfig import SYSTEM_CONFIG_DICT

# prediction_CFG
PREDICTION_TYPE_STRUCTURE_BASED = "structure"

PREDICTION_CFG_DICT = SYSTEM_CONFIG_DICT.get('prediction')

PREDICTION_SERVER_HOST = PREDICTION_CFG_DICT.get("serverHost")
PREDICTION_SERVER_TIMEOUT = PREDICTION_CFG_DICT.get("timeout")
PREDICTION_SERVER_MODEL_CFG = PREDICTION_CFG_DICT.get("modelCfg")