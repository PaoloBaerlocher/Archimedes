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

    def add(self, score, name):
        if (len(self.entries) < LB_MAX_ENTRIES or score > self.entries [LB_MAX_ENTRIES-1][0]):
            self.entries.append((score, name))
            self.entries.sort(reverse = True)

    def setDefaultEntries(self):
        self.clear()
        self.add(50000, "ARCHIE")
        self.add(45000, "PAOLO")
        self.add(40000, "MARC")
        self.add(35000, "FABRICE")
        self.add(30000, "FYB")
        self.add(25000, "JOHN")
        self.add(20000, "FABRICE")
        self.add(15000, "ARC ANGELS")
        self.add(10000, "FRED")
        self.add( 5000, "ZOZO")
