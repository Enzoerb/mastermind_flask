# mastermind_flask
this repo has 3 python scripts(game.py, game_mongodb.py and flask_api.py) and a templates folder


## game_mongodb.py
this script is in charge of doing CRUD operations to a MongoDB about the state of the games

### MastermindDB class
this is the only class in the script, their instance variables are client, base and collection
the client varible is an object from the class MongoClient imported from pymongo and has the client adress, the base variable gets the DB from client and the collection variable gets the collection from base

#### create_game
this function from MastermindDB generates a game_id and gets password(list of elements that is part of the game) as parameter. And then it creates a dictionary with all game required info, saving it as a document in self.collection

#### delete_game
this function gets the game_id as parameter and if it exists delete the game returning True, otherwise it returns False

#### find_game
find a game from it's game_id returning all the information

#### clear_all_games
clear all the games in collection, returning True if done and False if there is one ore more existing game not deleted

#### update_tries
asks the game_id and the list of tries as parameters, saving this list in the document with this game_id

#### update_password
asks the game_id and the password list as parameters, saving this list in the document with this game_id

#### get_tries
get the tries list from a document with the given game_id

#### get_password
get the password list from a document with the given game_id

#### delete_inactive
delete all games that have no tries in the last 10min


## game.py

### Mastermind class
this is the only class in the script, their instance variables are data_base and game_id
the data_base varible is an object from the class MastermindDB imported from game_mongodb and the game_id variable has the game_id from the game that is being played

#### generate_numbers
it is a staticmethod that creates, as default, four diferent random numbers to give an exemple of what the password will be

#### iniciate
it generates a password and calls the create_game function from MastermindDB, returning the game_id

#### guess_digits
this function accepts guesses and compares them with the password, adding the guess and the comparison to the tries list in the data_base and returning this list
if the game_id does not exists, the guess is right or the player reached the maximum amount of guesses the function returns a tuple with this information instead
##### exemple of comparison:
given number: 0512;
password: 0925;
output: 001;


## flask_api.py
this script display the game in a browser using flask

### home
this function display the homepage.html tamplate and can be called as '/', '/home', '/homepage' and '/mastermind'

### gera_numero
the function "gera_numero" calls the generate_numbers function from the Mastermind class and returns it using the gera_numeros.html tamplate
it can be called as '/gera_numero'

### inicia
the function "inicia" creates a new_player object from the Mastermind class and runs the iniciate function in it, returning the id with the inicia.html template
it can be called as '/inicia'

### get_id
this function displays the game_id.html tamplete that asks the user for a game_id
it can be called as '/tentativa'

### tentativa
if no guess is given it displays the waiting_guess.html template that asks the player for a guess
if a guess is given it runs the guess_digits function from the Mastermind class and returns tentativa.html template showing all the information. If the game has ended from any reason or there is no correspondent game_id it returns the lost_win.html template saying that
it can be called as '/tentativa/<int:game_id>?num=guess'


### clear_inactive
this function keeps running dunring all the execution calling the delete_inactive function from MastermindDB class
