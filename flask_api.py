from flask import Flask, request, render_template, url_for, flash, redirect
from multiprocessing import Process
from game import Mastermind
from forms import GuessNumberForm, EnterGameForm, CreateGameForm

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


@app.route("/inicia", methods=['GET', 'POST'])
def inicia():
    user_agent = str(request.user_agent)
    new_player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')

    game_id = 'waiting password'
    form = CreateGameForm()
    if form.validate_on_submit():
        game_id = new_player.iniciate()
        room_key = form.room_key.data
        new_player.create_roomkey(room_key)
        flash(f'Entered in game {game_id}')
        return redirect(url_for('tentativa', game_id=game_id))
    else:
        for error in form.confirm_roomkey.errors:
            flash(error)

    if 'curl' in user_agent:
        game_id = new_player.iniciate()
        curl_id = f'{game_id}\n'
        return curl_id

    template_id = render_template("inicia.html",
                                  title='inicia', form=form)
    return template_id


@app.route("/tentativa", methods=['GET', 'POST'])
def get_id():
    user_agent = str(request.user_agent)
    form = EnterGameForm()
    if form.validate_on_submit():
        game_id = form.game_id.data
        player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games', game_id)
        if not player.check_gameid():
            flash(f'Game id {game_id} not found')
            redirect(url_for("get_id"))
        elif not player.confirm_key(form.entered_key.data):
            flash(f'wrong password for room {game_id}')
            redirect(url_for("get_id"))
        else:
            flash(f'Entered in game {game_id}')
            return redirect(url_for('tentativa',
                                    game_id=game_id))

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

    else:
        curl_end = f'{response[0]}\npassword: {response[2]}\nlast_try: {response[3]}\n'
        end_template = render_template("lost_win.html",
                                       response=response,
                                       password=response[2],
                                       last_try=response[3],
                                       title='fim')
        return curl_end if "curl" in user_agent else end_template


def enter_key(player):
    game_id = player.game_id
    form = GuessNumberForm()
    if form.validate_on_submit():
        return redirect(url_for('tentativa',
                                game_id=game_id, num=form.guess.data))

    data_base = player.data_base
    tries = data_base.get_tries(game_id)
    if len(tries) == 0:
        template_keyerror = render_template("tentativa.html",
                                            tries=None,
                                            remaining=10,
                                            actual_try={'guess': 'Nothing Entered',
                                                        'response': 'Waiting First Guess'},
                                            title=f'tentativa 1',
                                            form=form)
    else:
        template_keyerror = render_template("tentativa.html",
                                            tries=tries,
                                            remaining=10-len(tries),
                                            actual_try=tries[-1],
                                            title=f'tentativa {len(tries)+1}',
                                            form=form)
    return template_keyerror


@app.route("/tentativa/<int:game_id>", methods=['GET', 'POST'])
def tentativa(game_id):
    user_agent = str(request.user_agent)
    player = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games', game_id)
    if not player.check_gameid():
        alert = f'Game id {player.game_id} not found\n'
        flash(alert)
        return alert if 'curl' in user_agent else redirect(url_for("get_id"))

    try:
        guess = request.args['num']
    except KeyError:
        curl_keyerror = f'please enter a guess in key \"num\"\n'
        template_keyerror = enter_key(player)
        return curl_keyerror if 'curl' in user_agent else template_keyerror

    form = GuessNumberForm()
    if form.validate_on_submit():
        return redirect(url_for('tentativa',
                                game_id=game_id, num=form.guess.data))

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
