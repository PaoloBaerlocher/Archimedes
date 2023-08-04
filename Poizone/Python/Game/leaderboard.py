import pygame
import json

LB_MAX_ENTRIES = 10

class Leaderboard(object):

    filename = "Leaderboard.json"       # Default filename
    entries = []

    def __init__(self, filename = ""):
        if (filename != ""):
            self.filename = filename

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                encoded = f.read()
                self.entries = json.loads(encoded)
        except FileNotFoundError:
            print("Leaderboard file not found. Set default entries.")
            self.setDefaultEntries()

    def save(self):
        with open(self.filename, 'w') as f:
            encoded = json.dumps(self.entries)
            f.write(encoded)

    def clear(self):
        self.entries = []

    def add(self, score, name, level):
        if (len(self.entries) < LB_MAX_ENTRIES or score > self.entries [LB_MAX_ENTRIES-1][0]):
            self.entries.append((score, name, level))
            self.entries.sort(reverse = True)

    def setDefaultEntries(self):
        self.clear()
        self.add(50000, "ARCHIE", 45)
        self.add(45000, "PAOLO",  40)
        self.add(40000, "MARC",   35)
        self.add(35000, "FABRICE", 30)
        self.add(30000, "FYB", 25)
        self.add(25000, "JOHN", 22)
        self.add(20000, "FABRICE", 20)
        self.add(15000, "ARC ANGELS", 15)
        self.add(10000, "FRED", 10)
        self.add( 5000, "ZOZO", 5)
