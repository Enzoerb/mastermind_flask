from flask import flash, request, render_template, redirect, url_for, session
from flask_bcrypt import Bcrypt
from game import Mastermind
from forms import GuessNumberForm
from flask_login import current_user

bcrypt = Bcrypt()


def check_invalid_registration(data_base, form):
    if data_base.check_username(form.username.data):
        flash(f'username "{form.username.data}" already in use')
    if data_base.check_email(form.email.data):
        flash(f'email "{form.email.data}" already in use')


def check_user_password(data_base, password):
    player = data_base.find_document(current_user.user_dict["username"], "username")
    if bcrypt.check_password_hash(player["password"], password):
        return True
    return False


def update_user_information(data_base, username, new_username, email, new_email):
    if data_base.update_username(username, new_username) or (new_username == username):
        flash('username updated')
        current_user.user_dict["username"] = new_username
    else:
        flash(f'username "{new_username}" already in use')
    if data_base.update_email(username, new_email) or (new_email == email):
        flash('email updated')
        current_user.user_dict["email"] = new_email
    else:
        flash(f'email {new_email} already in use')
    return redirect(url_for('account'))


def format_guess_response(response, form):
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
        if "game_id" in session:
            del session["game_id"]
        if "room_key" in session:
            del session["room_key"]
        curl_end = f'{response[0]}\npassword: {response[2]}\nlast_try: {response[3]}\n'
        end_template = render_template("lost_win.html",
                                       response=response,
                                       password=response[2],
                                       last_try=response[3],
                                       title='fim')
        return curl_end if "curl" in user_agent else end_template


def enter_guess(game):
    game_id = game.game_id
    form = GuessNumberForm()
    if form.validate_on_submit():
        template_keyerror = redirect(url_for('tentativa',
                                             game_id=game_id, num=form.guess.data))

    else:
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


def check_room_permission(game, game_id):
    if game.data_base.get_roomkey(game_id) == '':
        session["game_id"] = game_id
        return True
    if "game_id" in session:
        if str(session["game_id"]) != str(game_id):
            return False
    if "room_key" in session:
        if game.confirm_key(session["room_key"]):
            session["game_id"] = game_id
            return True

    return False


def clear_inactive():
    game = Mastermind('mongodb://localhost:27017/', 'mastermind', 'games')
    data_base = game.data_base
    while True:
        data_base.delete_inactive()
