#!/usr/bin/python
# -*- coding: utf-8 -*-


class Config():
    _instance = None
    _path = "private/config"

    def __init__(self):
        assert self._instance == None
        Config._instance = self

        self.__config = {}
        f = open(Config._path, "r")
        lines = f.readlines()
        for l in lines:
            s = l.split("#")[0].split("=")
            self.__config[s[0].strip()] = s[1].strip()
        f.close()

    @staticmethod
    def getInstance():
        if Config._instance == None:
            Config._instance = Config()

        return Config._instance

    def keys(self):
        return self.__config.keys()

    def __getitem__(self, key):
        return self.__config[key]

    def __setitem__(self, key, value):
        self.__config[key] = value

    def close(self):
        f = open(self.__path, "w")
        keys = self.__config.keys()
        for k in keys:
            f.write(k + "=" + self[k] + "\n")
        f.close()

if __name__ == "__main__":
    """Main de test"""
    c = Config.getInstance()
    keys = c.keys()
    for k in keys:
        print k + " = " + c[k]

    c["test"] = "tirlibibi"
    c.close()
