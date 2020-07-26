from abc import ABCMeta, abstractmethod
import memcache
from typing import List


class BaseCache(metaclass=ABCMeta):

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        pass


class MemCache(BaseCache):

    def __init__(self, servers: List, debug: bool):
        """

        @type debug: bool
        """
        self.__cache = memcache.Client(servers, debug=debug)

    def get(self, key: str):
        return self.__cache.get(key)

    def set(self, key: str, value: str):
        self.__cache.set(key, value)


class LocalDictCache(BaseCache):

    def __init__(self):
        self.__cache = {}

    def get(self, key: str):
        return self.__cache.get(key) if key is not None else None

    def set(self, key: str, value: str):
        if key is not None:
            self.__cache.set(key, value)
            ret = True
        else:
            ret = False
        return ret