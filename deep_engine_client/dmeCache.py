from .caching.cache import *
from configuration.sysConfig import CACHE_CONFIG_DICT

globalCache: BaseCache = MemCache(CACHE_CONFIG_DICT.get('servers'), CACHE_CONFIG_DICT.get('debug')) \
    if CACHE_CONFIG_DICT.get('type') == 'memcached' else LocalDictCache()
