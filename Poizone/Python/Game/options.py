import pygame
import json

class Options(object):

    filename = "Options.json"       # Default filename
    entries = {}

    def __init__(self, filename = ""):
        if (filename != ""):
            self.filename = filename

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                encoded = f.read()
                self.entries = json.loads(encoded)
        except FileNotFoundError:
            print("Options file not found. Set default entries.")
            self.setDefaultOptions()

    def save(self):
        with open(self.filename, 'w') as f:
            encoded = json.dumps(self.entries)
            f.write(encoded)

    def clear(self):
        self.entries = {}

    def setDefaultOptions(self):
        self.clear()
        self.setValue("VERSION", 1)
        self.setValue("SFX", True)
        self.setValue("MUSIC", True)

    def setValue(self, id, value):
        self.entries [id] = value

    def getValue(self, id):
        return self.entries [id]
