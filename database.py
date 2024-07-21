import json


class Database():
    def __init__(self):
        with open('database.json', 'r') as file:
            self.database = json.load(file)

    def get(self, key):
        return self.database[key]

    def set(self, key, value):
        self.database.update({key: value})

    def check_if_exists(self, key):
        return key in self.database

    def remove(self, key):
        del self.database[key]

    def save(self):
        with open('database.json', 'w') as file:
            json.dump(self.database, file)
