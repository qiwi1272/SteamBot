import time
import csv
import datetime
from driver_manager import ParallelDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as se
from bs4 import BeautifulSoup


CSMONEY_LOGIN_URL = 'https://auth.dota.trade/login?redirectUrl=https://cs.money/&callbackUrl=https://cs.money/login'


def steam_login(driver, username, password, twofa_method):
    # Create a WebDriverWait instance
    wait = WebDriverWait(driver, 1000) # Use WebDriverWait to wait for the input fields to be present

    input_fields = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "newlogindialog_TextInput_2eKVn"))
    )
    username_field = input_fields[0]
    password_field = input_fields[1]

    username_field.send_keys(username)
    password_field.send_keys(password)

    # Find and click the "Sign in" button by its CSS selector
    sign_in_button = driver.find_element(By.CSS_SELECTOR, ".newlogindialog_SubmitButton_2QgFE")
    sign_in_button.click()

    #2fa
    twofa_input_field = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "segmentedinputs_Input_HPSuA"))
    )
    def parse(s):
        _, twofa = s.split(':')
        return twofa
    
    twofa_code = parse(twofa_method())
    twofa_input_field.send_keys(twofa_code)

    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.btn_green_white_innerfade"))
    )
    sign_in_button.click()

    c00kies = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Popover_button-accept') and contains(@class, 'Button-module_primary') and contains(@class, 'Button-module_size-md') and contains(@class, 'Button-module_mode-fill') and contains(@class, 'Button-module_purple')]"))
    )
    # Click the button
    c00kies.click()


    inventory_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='styles_header__zp-6X']"))
    )
    inventory_tab.click()
    
    return False