from pymongo import MongoClient
from datetime import datetime


class MastermindDB:

    def __init__(self, client, base, collection):
        self.client = MongoClient(client)
        self.base = self.client[base]
        self.collection = self.base[collection]

    def create_game(self, password):
        game_id = 1
        while self.collection.find_one({"game_id": game_id}) != None:
            game_id += 1
        else:
            game = {"game_id": game_id, "password": password,
                    "tries": 0, "last_try": datetime.now()}
            self.collection.insert_one(game)

        return game_id

    def delete_game(self, game_id):
        game = self.collection.find_one({"game_id": game_id})
        if(game != None):
            self.collection.delete_one({"game_id": game_id})
            return True
        else:
            return False

    def find_game(self, game_id):
        return self.collection.find_one({"game_id": game_id})

    def clear_all_games(self):
        for document in self.collection.find():
            self.collection.delete_one(document)

        games = self.collection.estimated_document_count()
        return True if games == 0 else False

    def update_tries(self, game_id, tries):
        game = self.collection.find_one({"game_id": game_id})
        if(game != None):
            update = {"$set": {"tries": tries, "last_try": datetime.now()}}
            self.collection.update_one(game, update)
            return True
        else:
            return False

    def update_password(self, game_id, password):
        game = self.collection.find_one({"game_id": game_id})
        if(game != None):
            update = {"$set": {"password": password}}
            self.collection.update_one(game, update)
            return True
        else:
            return False

    def get_tries(self, game_id):
        game = self.collection.find_one({"game_id": game_id})
        return game["tries"] if game != None else None

    def get_password(self, game_id):
        game = self.collection.find_one({"game_id": game_id})
        return game["password"] if game != None else None

    def delete_inactive(self):
        deleted = 0

        for document in self.collection.find():
            time_inactive = datetime.now() - document["last_try"]
            minutes_inactive = time_inactive.total_seconds() / 60
            if(minutes_inactive > 10):
                self.collection.delete_one(document)
                deleted += 1

        return deleted


if __name__ == '__main__':
    DataBase = MastermindDB('mongodb://localhost:27017/', 'mastermind', 'games')
    DataBase.create_game([1, 2, 3, 4])
    print(DataBase.delete_inactive())
    print(DataBase.clear_all_games())
