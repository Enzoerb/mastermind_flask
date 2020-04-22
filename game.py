from game_mongodb import MastermindDB
from flask_bcrypt import Bcrypt
from random import randint
import os

bcrypt = Bcrypt()


class Mastermind:

    def __init__(self, client, base, collection, game_id=0):
        self.data_base = MastermindDB(client, base, collection)
        self.game_id = game_id

    @staticmethod
    def generate_numbers(length=4):
        numbers = set()
        while(len(numbers) < length):
            numbers.add(randint(0, 9))
        return list(numbers)

    @staticmethod
    def check_fix_guess(guess, password):
        if len(str(guess)) > len(password):
            to_remove = len(str(guess)) - 4
            guess = str(int(guess) // 10**to_remove)
        return guess

    @classmethod
    def check_password(cls, guess, password):

        guess = cls.check_fix_guess(guess, password)
        same_index = 0
        in_both = 0

        for index, digit in enumerate(guess):
            if str(digit) == str(password[index]):
                same_index += 1
            elif str(digit) in str(password):
                in_both += 1

        response = "0"*in_both + "1"*same_index
        return response

    def iniciate(self):
        password = self.generate_numbers()
        self.game_id = self.data_base.create_game(list(password))
        return f'{self.game_id}'

    def create_roomkey(self, entered_key):
        if entered_key != '':
            room_key = bcrypt.generate_password_hash(entered_key).decode('utf-8')
            self.data_base.update_roomkey(self.game_id, room_key)
        else:
            self.data_base.update_roomkey(self.game_id, '')

    def add_try(self, guess, response):
        actual_try = dict()
        actual_try["guess"] = guess
        actual_try["response"] = response

        tries = self.data_base.get_tries(self.game_id)
        tries.append(actual_try)
        self.data_base.update_tries(self.game_id, tries)

    def check_gameid(self):
        game = self.data_base.find_document(self.game_id, "game_id")
        if game == None:
            return False
        return True

    def guess_digits(self, guess):

        game = self.data_base.find_document(self.game_id, "game_id")
        password = self.data_base.get_password(self.game_id)
        guess = self.check_fix_guess(guess, password)
        response = self.check_password(guess, password)
        self.add_try(guess, response)
        tries = self.data_base.get_tries(self.game_id)

        if(response == "1"*len(password)):
            self.data_base.delete_document(self.game_id, "game_id")
            return (f"Congrats!! you guessed it with {len(tries)} tries", "green",
                    password, tries[-1])
        elif len(tries) >= 10:
            self.data_base.delete_document(self.game_id, "game_id")
            return ("you lost, try again", "red",
                    password, tries[-1])

        return tries

    def confirm_key(self, entered_key):
        room_key = self.data_base.get_roomkey(self.game_id)
        if room_key == '':
            return True
        elif entered_key != '':
            check_key = bcrypt.check_password_hash(room_key, entered_key)
            return check_key
        else:
            return False


if __name__ == '__main__':
    Game = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')
    guess = Game.generate_numbers()
    Game.iniciate()
    print(Game.guess_digits(guess))
    Game.data_base.delete_document(Game.game_id, "game_id")
