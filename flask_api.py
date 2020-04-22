from flask import Flask, request, render_template, url_for, flash, redirect, session
from multiprocessing import Process
from game import Mastermind
from game_mongodb import PlayerDB, UserLogin
from forms import GuessNumberForm, EnterGameForm, CreateGameForm, GenerateNumberForm, LoginForm, RegistrationForm, AccountUpdateForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '5b23e4fb78c69bca36a88002b9879755'
bcrypt = Bcrypt()
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_dict):
    return UserLogin(user_dict)


@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
@app.route("/homepage", methods=['GET'])
@app.route("/mastermind", methods=['GET'])
def home():
    user_agent = str(request.user_agent)
    curl_homepage = 'HomePage\n'
    template_homepage = render_template('homepage.html')
    return curl_homepage if "curl" in user_agent else template_homepage


def check_invalid_registration(data_base, form):
    if data_base.check_username(form.username.data):
        flash(f'username "{form.username.data}" already in use')
        invalid.append('username')
    if data_base.check_email(form.email.data):
        flash(f'email "{form.email.data}" already in use')
        invalid.append('email')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        data_base = PlayerDB('mongodb://localhost:27017/', 'mastermind', 'players')
        if data_base.create_player(form.username.data, form.email.data, hashed_password):
            flash(f'account created for {form.username.data}')
            player = data_base.find_document(form.username.data, "username")
            login_user(UserLogin({key: player[key]
                                  for key in player if key not in ('_id', 'password')}))
            return redirect(url_for('home'))
        else:
            check_invalid_registration(data_base, form)
        return redirect(url_for('register', form=form))

    return render_template('register.html',
                           title='register',
                           form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        data_base = PlayerDB('mongodb://localhost:27017/', 'mastermind', 'players')
        player = data_base.find_document(form.username.data, 'username')
        if player == None:
            flash(f'username "{form.username.data}" does not exist')
            return redirect(url_for('login'))
        else:
            check = True
            if player["email"] != form.email.data:
                flash(f'wrong email ({form.email.data}) for username "{form.username.data}"')
                check = False
            if not bcrypt.check_password_hash(player["password"], form.password.data):
                flash(f'wrong password for username "{form.username.data}"')
                check = False
            if not check:
                return redirect(url_for('login'))
            else:
                flash('logged in')
                login_user(UserLogin({key: player[key]
                                      for key in player if key not in ('_id', 'password')}))
                return redirect(url_for('home'))

    return render_template('login.html',
                           title='login',
                           form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="account")


def check_password(password):
    data_base = PlayerDB('mongodb://localhost:27017/', 'mastermind', 'players')
    player = data_base.find_document(current_user.user_dict["username"], "username")
    if bcrypt.check_password_hash(player["password"], password):
        return True
    return False


@app.route("/account/update", methods=['GET', 'POST'])
@login_required
def account_update():
    username = current_user.user_dict["username"]
    user_email = current_user.user_dict["email"]
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if not check_password(form.password.data):
            flash('wrong password')
            return redirect(url_for('account_update'))
        data_base = PlayerDB('mongodb://localhost:27017/', 'mastermind', 'players')
        if form.email.data == user_email and form.username.data == username:
            current_user.user_dict["username"] = form.username.data
            current_user.user_dict["email"] = form.email.data
            flash('information sucessfully updated')
            return redirect(url_for('account'))
        elif form.email.data == user_email:
            if data_base.check_username(form.username.data):
                flash(f'username "{form.username.data}" already in use')
                return redirect(url_for('account_update'))
            else:
                current_user.user_dict["username"] = form.username.data
                current_user.user_dict["email"] = form.email.data
                data_base.update_username(username, form.username.data)
                flash('information sucessfully updated')
                return redirect(url_for('account'))
        elif form.username.data == username:
            if data_base.check_email(form.email.data):
                flash(f'email "{form.email.data}" already in use')
                return redirect(url_for('account_update'))
            else:
                current_user.user_dict["username"] = form.username.data
                current_user.user_dict["email"] = form.email.data
                data_base.update_email(username, form.email.data)
                flash('information sucessfully updated')
                return redirect(url_for('account'))
        else:
            check = True
            if data_base.check_username(form.username.data):
                flash(f'username "{form.username.data}" already in use')
                check = False
            if data_base.check_email(form.email.data):
                flash(f'email "{form.email.data}" already in use')
                check = False
            if not check:
                return redirect(url_for('account_update'))
            else:
                current_user.user_dict["username"] = form.username.data
                current_user.user_dict["email"] = form.email.data
                data_base.update_username(username, form.username.data)
                data_base.update_email(username, form.email.data)
                flash('information sucessfully updated')
                return redirect(url_for('account'))

    elif request.method == "GET":
        form.username.data = username
        form.email.data = user_email

    return render_template("update.html", title="update", form=form)


@app.route("/gera_numero", methods=['GET', 'POST'])
def gera_numero():
    form = GenerateNumberForm()
    user_agent = str(request.user_agent)
    numbers = Mastermind.generate_numbers()
    curl_numbers = f'{numbers}\n'
    if form.validate_on_submit():
        return redirect(url_for("gera_numero"))
    template_numbers = render_template('gera_numeros.html',
                                       numeros=numbers,
                                       title='gerador',
                                       form=form)
    return curl_numbers if "curl" in user_agent else template_numbers


@app.route("/inicia", methods=['GET', 'POST'])
def inicia():
    user_agent = str(request.user_agent)
    new_game = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')

    game_id = 'waiting password'
    form = CreateGameForm()
    if form.validate_on_submit():
        game_id = new_game.iniciate()
        room_key = form.room_key.data
        new_game.create_roomkey(room_key)
        session["game_id"] = game_id
        session["room_key"] = room_key
        flash(f'Created game {game_id}')
        return redirect(url_for('tentativa', game_id=game_id))
    else:
        for error in form.confirm_roomkey.errors:
            flash(error)

    if 'curl' in user_agent:
        game_id = new_game.iniciate()
        session["game_id"] = game_id
        session["room_key"] = ''
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
        entered_key = form.entered_key.data
        game = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games', game_id)
        if not game.check_gameid():
            flash(f'Game id {game_id} not found')
            redirect(url_for("get_id"))
        elif not game.confirm_key(entered_key):
            flash(f'wrong password for room {game_id}')
            redirect(url_for("get_id"))
        else:
            session["game_id"] = game_id
            session["room_key"] = entered_key
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
        del session["game_id"]
        del session["room_key"]
        curl_end = f'{response[0]}\npassword: {response[2]}\nlast_try: {response[3]}\n'
        end_template = render_template("lost_win.html",
                                       response=response,
                                       password=response[2],
                                       last_try=response[3],
                                       title='fim')
        return curl_end if "curl" in user_agent else end_template


def enter_key(game):
    game_id = game.game_id
    form = GuessNumberForm()
    if form.validate_on_submit():
        return redirect(url_for('tentativa',
                                game_id=game_id, num=form.guess.data))

    data_base = game.data_base
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


def check_permission(game, game_id):
    if "game_id" in session:
        if str(session["game_id"]) != str(game_id):
            return False
    if "room_key" in session:
        if game.confirm_key(session["room_key"]):
            session["game_id"] = game_id
            return True

    return False


@app.route("/tentativa/<int:game_id>", methods=['GET', 'POST'])
def tentativa(game_id):
    user_agent = str(request.user_agent)
    game = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games', game_id)
    if not game.check_gameid():
        alert = f'Game id {game.game_id} not found\n'
        flash(alert)
        return alert if 'curl' in user_agent else redirect(url_for("get_id"))

    if not check_permission(game, game_id):
        alert = 'please enter the password'
        curl_alert = 'make sure you created the game and it has no password\n'
        flash(alert)
        return curl_alert if 'curl' in user_agent else redirect(url_for("get_id"))

    try:
        guess = request.args['num']
    except KeyError:
        curl_keyerror = f'please enter a guess in key \"num\"\n'
        template_keyerror = enter_key(game)
        return curl_keyerror if 'curl' in user_agent else template_keyerror

    form = GuessNumberForm()
    if form.validate_on_submit():
        return redirect(url_for('tentativa',
                                game_id=game_id, num=form.guess.data))

    response = game.guess_digits(guess)
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
