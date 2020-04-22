from pymongo import MongoClient
from datetime import datetime
from flask_login import UserMixin, LoginManager


class UserLogin(UserMixin):

    def __init__(self, user_dict):
        self.user_dict = user_dict

    def get_id(self):
        return self.user_dict


class DefaultDB:

    def __init__(self, client, base, collection):
        self.client = MongoClient(client)
        self.base = self.client[base]
        self.collection = self.base[collection]

    def delete_document(self, document_id, id_name):
        document = self.collection.find_one({f"{id_name}": document_id})
        if(document != None):
            self.collection.delete_one({f"{id_name}": document_id})
            return True
        else:
            return False

    def find_document(self, document_id, id_name):
        return self.collection.find_one({f"{id_name}": document_id})

    def clear_all_documents(self):
        for document in self.collection.find():
            self.collection.delete_one(document)

        document = self.collection.estimated_document_count()
        return True if document == 0 else False


class MastermindDB(DefaultDB):

    def create_game(self, password):
        game_id = 1
        while self.collection.find_one({"game_id": game_id}) != None:
            game_id += 1
        else:
            game = {"game_id": game_id, "room_key": '', "password": password,
                    "tries": list(), "last_try": datetime.now()}
            self.collection.insert_one(game)

        return game_id

    def update_tries(self, game_id, tries):
        game = self.collection.find_one({"game_id": game_id})
        if(game != None):
            update = {"$set": {"tries": tries, "last_try": datetime.now()}}
            self.collection.update_one(game, update)
            return True
        return False

    def update_password(self, game_id, password):
        game = self.collection.find_one({"game_id": game_id})
        if(game != None):
            update = {"$set": {"password": password}}
            self.collection.update_one(game, update)
            return True
        return False

    def update_roomkey(self, game_id, room_key):
        game = self.collection.find_one({"game_id": game_id})
        if(game != None):
            update = {"$set": {"room_key": room_key}}
            self.collection.update_one(game, update)
            return True
        return False

    def get_tries(self, game_id):
        game = self.collection.find_one({"game_id": game_id})
        return game["tries"] if game != None else None

    def get_password(self, game_id):
        game = self.collection.find_one({"game_id": game_id})
        return game["password"] if game != None else None

    def get_roomkey(self, game_id):
        game = self.collection.find_one({"game_id": game_id})
        return game["room_key"] if game != None else None

    def delete_inactive(self):
        deleted = 0

        for document in self.collection.find():
            time_inactive = datetime.now() - document["last_try"]
            minutes_inactive = time_inactive.total_seconds() / 60
            if(minutes_inactive > 10):
                self.collection.delete_one(document)
                deleted += 1

        return deleted


class PlayerDB(DefaultDB):

    def check_username(self, username):
        player = self.collection.find_one({"username": username})
        if player == None:
            return False
        return True

    def check_email(self, email):
        player = self.collection.find_one({"email": email})
        if player == None:
            return False
        return True

    def create_player(self, username, email, password):
        if (not self.check_username(username)) and (not self.check_email(email)):
            player = {"username": username, "password": password,
                      "email": email, "wins": 0}
            self.collection.insert_one(player)
            return True
        return False

    def update_username(self, username, new_username):
        player = self.collection.find_one({"username": username})
        if self.check_username(new_username):
            return False
        if player != None:
            update = {"$set": {"username": new_username}}
            self.collection.update_one(player, update)
            return True
        return False

    def update_email(self, username, new_email):
        player = self.collection.find_one({"username": username})
        if self.check_email(new_email):
            return False
        if player != None:
            update = {"$set": {"email": new_email}}
            self.collection.update_one(player, update)
            return True
        return False

    def update_password(self, username, new_password):
        player = self.collection.find_one({"username": username})
        if player != None:
            update = {"$set": {"password": new_password}}
            self.collection.update_one(player, update)
            return True
        return False

    def update_wins(self, username, new_wins):
        player = self.collection.find_one({"username": username})
        if player != None:
            update = {"$set": {"wins": new_wins}}
            self.collection.update_one(player, update)
            return True
        return False

    def get_username(self, username):
        player = self.collection.find_one({"username": username})
        return player["username"] if game != None else None

    def get_email(self, username):
        player = self.collection.find_one({"username": username})
        return player["email"] if game != None else None

    def get_password(self, username):
        player = self.collection.find_one({"username": username})
        return player["password"] if game != None else None

    def get_email(self, username):
        player = self.collection.find_one({"username": username})
        return player["wins"] if game != None else None


if __name__ == '__main__':
    DataBase = PlayerDB('mongodb://localhost:27017/', 'mastermind', 'playerss')
    DataBase.create_player('username', 'email', 'password')
    player = DataBase.find_document('username', 'username')
    print(player)
    DataBase.delete_document('username', 'username')
    player = DataBase.find_document('username', 'username')
    print(player)
