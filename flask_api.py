from flask import Flask, request, render_template
from game import Mastermind
from multiprocessing import Process

app = Flask(__name__)


@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
@app.route("/homepage", methods=['GET'])
@app.route("/mastermind", methods=['GET'])
def home():
    user_agent = str(request.user_agent)
    curl_homepage = 'HomePage\n'
    template_homepage = render_template('homepage.html')
    return curl_homepage if "curl" in user_agent else template_homepage


@app.route("/gera_numero", methods=['GET'])
def gera_numero():
    user_agent = str(request.user_agent)
    numbers = Mastermind.generate_numbers()
    curl_numbers = f'{numbers}\n'
    template_numbers = render_template('gera_numeros.html',
                                       numeros=numbers,
                                       title='gerador')
    return curl_numbers if "curl" in user_agent else template_numbers


@app.route("/inicia", methods=['GET'])
def inicia():
    user_agent = str(request.user_agent)
    new_player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')
    id = new_player.iniciate()
    curl_id = f'{id}\n'
    template_id = render_template("inicia.html", id=id, title='inicia')
    return curl_id if "curl" in user_agent else template_id


@app.route("/tentativa", methods=['GET'])
def get_id():
    user_agent = str(request.user_agent)
    curl_no_gameid = 'please enter a game id\n'
    template_no_gameid = render_template("game_id.html", title='game id')
    return curl_no_gameid if "curl" in user_agent else template_no_gameid


@app.route("/tentativa/<int:game_id>", methods=['GET'])
def tentativa(game_id):
    user_agent = str(request.user_agent)
    try:
        guess = request.args['num']
    except KeyError:
        curl_keyerror = f'please enter a guess in key \"num\"\n'
        template_keyerror = render_template("waiting_guess.html",
                                            title='palpite')
        return curl_keyerror if "curl" in user_agent else template_keyerror

    player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games',
                        game_id)
    response = player.guess_digits(guess)

    curl_game = f'{response[-1]}\n'
    game_template = render_template("tentativa.html",
                                    tries=response,
                                    remaining=10-len(response),
                                    actual_try=response[-1],
                                    title=f'tentativa {len(response)+1}')

    curl_end = f'{response[0]}\n'
    end_template = render_template("lost_win.html",
                                   response=response,
                                   title='fim')

    if type(response) == type(list()):
        return curl_game if "curl" in user_agent else game_template
    else:
        return curl_end if "curl" in user_agent else end_template


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
