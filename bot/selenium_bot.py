from selenium import webdriver
from player import play, create_game

with webdriver.Firefox() as driver:
    driver.get("http://www.localhost:5000")
    driver.fullscreen_window()
    create_game(driver)
    while True:
        if not play(driver):
            break
