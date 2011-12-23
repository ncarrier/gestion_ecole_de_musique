#!/usr/bin/python
# -*- coding: utf-8 -*-

class Config():
	# TODO en faire un singleton ? protéger contre les accès multiples ?
	def __init__(self, path):
		self.__path = path
		self.__config = {}
		f = open(self.__path, "r")
		lines = f.readlines()
		for l in lines:
			s = l.split("=")
			self.__config[s[0].strip()] = s[1].strip()
		f.close()

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
	c = Config("private/config")
	keys = c.keys()
	for k in keys:
		print k + " = " + c[k]
	
	c["test"] = "tirlibibi"
	c.close()
