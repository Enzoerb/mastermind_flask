from flask import Flask, request, render_template, url_for, flash, redirect
from multiprocessing import Process
from game import Mastermind
from forms import GuessNumberForm, GetIdForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '5b23e4fb78c69bca36a88002b9879755'


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


@app.route("/tentativa", methods=['GET', 'POST'])
def get_id():
    user_agent = str(request.user_agent)
    form = GetIdForm()
    if form.validate_on_submit():
        return redirect(url_for('tentativa',
                                game_id=form.game_id.data))

    curl_no_gameid = 'please enter a game id\n'
    template_no_gameid = render_template("game_id.html",
                                         title='game id', form=form)
    return curl_no_gameid if "curl" in user_agent else template_no_gameid


def format_response(response, form):
    user_agent = str(request.user_agent)
    if type(response) == type(list()):
        curl_game = f'remaining:{10-len(response)}\n{response[-1]}\n'
        game_template = render_template("tentativa.html",
                                        tries=response,
                                        remaining=10-len(response),
                                        actual_try=response[-1],
                                        title=f'tentativa {len(response)+1}',
                                        form=form)
        return curl_game if "curl" in user_agent else game_template

    elif len(response) > 2:
        curl_end = f'{response[0]}\npassword: {response[2]}\nlast_try: {response[3]}\n'
        end_template = render_template("lost_win.html",
                                       response=response,
                                       password=response[2],
                                       last_try=response[3],
                                       title='fim')
        return curl_end if "curl" in user_agent else end_template

    else:
        curl_notfound = f'{response[0]}\n'
        notfound_template = render_template("id_notfound.html",
                                            response=response,
                                            title='not found')
        return curl_notfound if "curl" in user_agent else notfound_template


@app.route("/enter_key/<int:game_id>", methods=['GET', 'POST'])
def enter_key(game_id):
    form = GuessNumberForm()
    if form.validate_on_submit():
        return redirect(url_for('tentativa',
                                game_id=game_id, num=form.guess.data))

    template_keyerror = render_template("waiting_guess.html",
                                        title='palpite', form=form)
    return template_keyerror


@app.route("/tentativa/<int:game_id>", methods=['GET', 'POST'])
def tentativa(game_id):
    user_agent = str(request.user_agent)
    try:
        guess = request.args['num']
    except KeyError:
        curl_keyerror = f'please enter a guess in key \"num\"\n'
        not_curl = redirect(url_for("enter_key", game_id=game_id))
        return curl_keyerror if 'curl' in user_agent else not_curl

    form = GuessNumberForm()
    if form.validate_on_submit():
        return redirect(url_for('tentativa',
                                game_id=game_id, num=form.guess.data))

    player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games', game_id)
    response = player.guess_digits(guess)
    formatted_response = format_response(response, form)
    return formatted_response


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
