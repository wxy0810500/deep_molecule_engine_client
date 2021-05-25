from configuration.sysConfig import SYSTEM_CONFIG_DICT

# prediction_CFG
PREDICTION_CFG_DICT = SYSTEM_CONFIG_DICT.get('prediction')

PREDICTION_SERVER_HOST = PREDICTION_CFG_DICT.get("serverHost")
PREDICTION_SERVER_TIMEOUT = PREDICTION_CFG_DICT.get("timeout")
PREDICTION_SERVER_MODEL_CFG = PREDICTION_CFG_DICT.get("modelCfg")

PREDICTION_TYPE_LIGAND = "ligand"
PREDICTION_TYPE_NETWORK = "network"

LIGAND_MODEL_CFG = dict((model, data[0]) for model, data in
                        PREDICTION_SERVER_MODEL_CFG.get(PREDICTION_TYPE_LIGAND).items())

NETWORK_MODEL_CFG = dict((model, data[0]) for model, data in
                         PREDICTION_SERVER_MODEL_CFG.get(PREDICTION_TYPE_NETWORK).items())
