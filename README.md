# mastermind_flask

## flask_api.py
this flask api has three functions(gera_numero, inicia and tentativa)
### gera_numero
the function "gera_nummero" calls the random_set function from the random_set module(described bellow) and returns the output as a string
### inicia
the function "inicia" calls the random_set function from the random_set module saving the digits in the output into a .txt file and returns 'OK'
### tentativa
given a number the "tentativa" function compares it with the one saved in the password.txt file and returns (1)how many digits are in the same position and (0)how many digits are in both numbers but not in same position
#### exemple:
given number: 0512
password: 0925
output: 001

## random_set.py
random_set.py has only the random_set function

### random_set function
generate a set with 'n' diferent numbers and returns it, 'n' being a parameter given to the function
