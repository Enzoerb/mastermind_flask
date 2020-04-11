from game_mongodb import MastermindDB
from random import randint
import pymongo
import os


class Mastermind:

    def __init__(self, client, base, collection, game_id=0):
        self.data_base = MastermindDB(client, base, collection)
        self.game_id = game_id

    @staticmethod
    def generate_numbers(length=4):
        numbers = set()
        while(len(numbers) < length):
            numbers.add(randint(0, 9))
        return numbers

    def iniciate(self):
        password = self.generate_numbers()
        self.game_id = self.data_base.create_game(list(password))
        return f'Game ID: {self.game_id}'

    def guess_digits(self, guess):

        game = self.data_base.find_game(self.game_id)
        if game == None:
            return 'Game not found, wrong id'

        tries = self.data_base.get_tries(self.game_id)
        tries += 1
        self.data_base.update_tries(self.game_id, tries)

        in_both = 0
        same_index = 0
        password = self.data_base.get_password(self.game_id)

        for index, digit in enumerate(guess):
            if str(digit) == str(password[index]):
                same_index += 1
            elif str(digit) in str(password):
                in_both += 1

        if(same_index == len(password)):
            self.data_base.delete_game(self.game_id)
            return f"Congrats!! you guessed it with {tries} tries"
        elif tries >= 10:
            self.data_base.delete_game(self.game_id)
            return "you lost, try again"
        return "0"*in_both + "1"*same_index


if __name__ == '__main__':
    Game = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')
    guess = Game.generate_numbers()
    Game.iniciate()
    print(Game.guess_digits(guess))
    Game.data_base.delete_game(Game.game_id)
