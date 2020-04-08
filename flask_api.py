from flask import Flask, request
from random_set import random_set
import os

app = Flask(__name__)


@app.route("/gera_numero")
def gera_numero():
    return f'{random_set(4)}'


@app.route("/inicia")
def inicia():
    local_path = os.getcwd()
    file_path = os.path.join(local_path, 'password.txt')
    with open(file_path, 'w') as file:
        password = random_set(4)
        for digit in password:
            file.write(str(digit))
        file.write('\n')
    return 'OK'


@app.route("/tentativa", methods=['GET'])
def tentativa():

    try:
        guess = request.args['num']
    except KeyError:
        return 'please submit a number in the key \"num\"'

    zeros = 0
    ones = 0
    local_path = os.getcwd()
    file_path = os.path.join(local_path, 'password.txt')

    with open(file_path, 'r') as file:
        password = file.readline()

    for index, digit in enumerate(guess):
        if digit == password[index]:
            ones += 1
        elif digit in password:
            zeros += 1

    return "0"*zeros + "1"*ones


if __name__ == '__main__':
    app.run(debug=True)
