from flask import Flask, request, render_template
from game import Mastermind
from multiprocessing import Process

app = Flask(__name__)


@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
@app.route("/homepage", methods=['GET'])
@app.route("/mastermind", methods=['GET'])
def home():
    return render_template('homepage.html')


@app.route("/gera_numero", methods=['GET'])
def gera_numero():
    return render_template('gera_numeros.html',
                           numeros=Mastermind.generate_numbers(),
                           title='gerador')


@app.route("/inicia", methods=['GET'])
def inicia():
    global new_player
    new_player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')
    return render_template("inicia.html",
                           id=new_player.iniciate(), title='inicia')


@app.route("/tentativa", methods=['GET'])
def get_id():
    return render_template("game_id.html")


@app.route("/tentativa/<int:game_id>", methods=['GET'])
def tentativa(game_id):

    try:
        guess = request.args['num']
    except KeyError:
        return render_template("waiting_guess.html")

    player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games', game_id)
    response = player.guess_digits(guess)
    if type(response) == type(list()):
        return render_template("tentativa.html",
                               tries=response,
                               remaining=10-len(response),
                               actual_try=response[-1],
                               title=f'tentativa {len(response)+1}')
    else:
        return render_template("lost_win.html",
                               response=response,
                               title='end')


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
