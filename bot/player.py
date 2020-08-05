from selenium.common.exceptions import NoSuchElementException
from random import sample
from os.path import exists


def generate_guess():
    return "".join(map(str, sample(range(0, 9), 4)))


def create_game(driver):
    driver.get("http://www.localhost:5000/inicia")
    key = driver.find_element_by_name("room_key")
    confirm_key = driver.find_element_by_name("confirm_roomkey")
    button = driver.find_element_by_name("submit")
    room_key = "1234"
    key.clear()
    key.send_keys(room_key)
    confirm_key.clear()
    confirm_key.send_keys(room_key)
    button.click()


def end(driver, result):
    n = 1
    while exists(f'screenshots/{result}_{n}.png'):
        n += 1
    driver.save_screenshot(f'screenshots/{result}_{n}.png')


def submit_guess(driver, guess):
    input_place = driver.find_element_by_name("guess")
    submit_button = driver.find_element_by_name("submit")
    driver.implicitly_wait(0.5)
    input_place.clear()
    input_place.send_keys(guess)
    submit_button.click()


def play(driver):
    try:
        key = driver.find_element_by_id('state')
        if key.text[:8] == 'Congrats':
            end(driver, 'win')
            return False
        else:
            end(driver, 'lost')
            return False
    except NoSuchElementException:
        pass
    try:
        guess = generate_guess()
        submit_guess(driver, guess)
        return True
    except NoSuchElementException:
        return False
    return True
