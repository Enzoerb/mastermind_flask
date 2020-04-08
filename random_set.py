from random import randint


def random_set(length):

    numbers = set()
    while(len(numbers) < length):
        numbers.add(randint(0, 9))
    return numbers


if __name__ == '__main__':
    numbers = random_set(4)
    print(numbers)
