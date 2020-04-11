from flask import Flask, request
from game import Mastermind
from multiprocessing import Process

app = Flask(__name__)


@app.route("/gera_numero", methods=['GET'])
def gera_numero():
    return f'{Mastermind.generate_numbers()}'


@app.route("/inicia", methods=['GET'])
def inicia():
    global new_player
    new_player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')
    return f'{new_player.iniciate()}'


@app.route("/tentativa/<int:game_id>", methods=['GET'])
def tentativa(game_id):

    try:
        guess = request.args['num']
    except KeyError:
        return 'please submit a number in the key \"num\"'

    player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games', game_id)
    return f'{player.guess_digits(guess)}'


def clear_inactive():
    game = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')
    data_base = game.data_base
    while True:
        data_base.delete_inactive()


if __name__ == '__main__':

    p = Process(target=clear_inactive)
    p.start()
    app.run(debug=True, use_reloader=False)
    p.join()
