#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["nombre"]

nombre = {0 : u"zéro",
          1 : "un",
          2 : "deux",
          3 : "trois",
          4 : "quatre",
          5 : "cinq",
          6 : "six",
          7 : "sept",
          8 : "huit",
          9 : "neuf",
          10 : "dix",
          11 : "onze",
          12 : "douze",
          13 : "treize",
          14 : "quatorze",
          15 : "quinze",
          16 : "seize",
          17 : "dix-sept",
          18 : "dix-huit",
          19 : "dix-neuf",
          20 : "vingt",
          21 : "vingt et un",
          22 : "vingt deux",
          23 : "vingt trois",
          24 : "vingt quatre",
          25 : "vingt cinq",
          26 : "vingt six",
          27 : "vingt sept",
          28 : "vingt huit",
          29 : "vingt neuf",
          30 : "trente",
          31 : "trente et un",
          32 : "trente deux",
          33 : "trente trois",
          34 : "trente quatre",
          35 : "trente cinq",
          36 : "trente six",
          37 : "trente sept",
          38 : "trente huit",
          39 : "trente neuf",
          40 : "quarante",
          41 : "quarante et un",
          42 : "quarante deux",
          43 : "quarante trois",
          44 : "quarante quatre",
          45 : "quarante cinq"}

if __name__ == "__main__":
    """Main de test"""
    for i in range(0, 45):
        print str(i) + " : " + nombre[i]
