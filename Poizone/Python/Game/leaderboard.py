import pygame
import json

LB_MAX_ENTRIES = 10
LB_MAX_NAME_LENGTH = 10

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

    def canEnter(self, score):
        return (len(self.entries) < LB_MAX_ENTRIES) or (score > self.entries [LB_MAX_ENTRIES-1][0])

    def add(self, score, name, level):
        if self.canEnter(score):
            self.entries.append([score, name, level])
            self.entries.sort(reverse = True)

    def setDefaultEntries(self):
        self.clear()
        self.add(40000, "ARCHIMEDES", 45)
        self.add(30000, "PAOLO",  40)
        self.add(25000, "MARC",   35)
        self.add(20000, "FABRICE H", 30)
        self.add(15000, "FYB", 25)
        self.add(10000, "JOHN", 20)
        self.add( 5000, "FABRICE M", 10)
        self.add( 4000, "ARC ANGELS", 9)
        self.add( 3000, "FRED", 7)
        self.add( 2000, "ZOZO", 5)
