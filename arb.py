import time
import csv
import driver_manager as driver_manager
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as se
from bs4 import BeautifulSoup

login_url = 'https://steamcommunity.com/login/home/'


drivers = driver_manager.ParallelDriverManager(threads=1)

def login(driver, cred):
    login = cred.split(':')
    driver.get(login_url)
    # Create a WebDriverWait instance
    wait = WebDriverWait(driver, 10) # Use WebDriverWait to wait for the input fields to be present
    input_fields = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "newlogindialog_TextInput_2eKVn"))
    )
    username = input_fields[0]
    password = input_fields[1]

    username.send_keys(login[0])
    password.send_keys(login[1])

    # Find and click the "Sign in" button by its CSS selector
    sign_in_button = driver.find_element(By.CSS_SELECTOR, ".newlogindialog_SubmitButton_2QgFE")
    sign_in_button.click()

    while(driver.current_url == login_url): # TODO: auto 2fa
        time.sleep(1)

    return False

def extract_price(input_string):
    lines = input_string.split('\n')
    if len(lines) >= 2:
        try:
            currency, price = lines[1].split('$')
            price = price[1:]
        except ValueError:
            currency = lines[1][0]
            price = lines[1][1:]
        return price, currency
    return None

def scrape_market(driver):
    # Create a list to store item information
    names = []
    last_names = []

    while True:
        # Wait logic
        try:
            # for listing element
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchResultsRows"))
            )
            # for steam javascript
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("return getComputedStyle(document.getElementById('searchResultsRows')).opacity === '1';")
            )
        except se.TimeoutException:
            driver.refresh()
            time.sleep(1)
            continue
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Find all the items in the HTML
        items = soup.find_all('div', {'class': 'market_listing_row market_recent_listing_row market_listing_searchresult'})

        # Iterate through the items and extract information
        temp_items = []
        for item in items:
            item_name = item.find('span', {'class': 'market_listing_item_name'}).text.strip()
            item_listing = item.find('span', {'class': 'market_listing_num_listings_qty'}).text.strip()
            item_price = item.find('span', {'class': 'normal_price'}).text.strip()
            item_price, currency = extract_price(item_price)
            temp_items.append([item_name, item_listing, item_price, currency])
        
        if not temp_items:
            driver.refresh()
            time.sleep(1)
            continue
        elif temp_items != last_names:
            last_names = temp_items
            for item in temp_items:
                item.append(datetime.datetime.now())
                names.append(item)
            temp_items = []
            

        end_element = soup.find('span', {'id': 'searchResults_end'})
        total_element = soup.find('span', {'id': 'searchResults_total'})

        if end_element and total_element:
            end = int(end_element.text.strip())
            total = int(total_element.text.strip())

            # Check if we have reached the last page
            if end == total:
                break

            url = driver.current_url
            if '#' in url:
                url, page = url.split('#')
                # Find the numeric part of the page string
                page_numeric = int(''.join(filter(str.isdigit, page)))
                # Increment the numeric part
                page_numeric += 1
                # Format the page string with the incremented numeric part
                page = f'#p{page_numeric}_price_asc'
                driver.get(url + page)
                time.sleep(1)
                continue
            else:
                driver.get(url + '#p1_price_asc')
                time.sleep(1)
                continue
        else:
            driver.refresh()
            continue

    return names

def scrape_item(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hover_item_name"))
    )
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    if soup.find('div', {'class': 'market_listing_table_message'}).text.strip():
        while soup.find('div', {'class': 'market_listing_table_message'}).text.strip().startswith('There was an error'):
            driver.refresh()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hover_item_name"))
            )
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all the items in the HTML
    item_name = soup.find('h1', {'class': 'hover_item_name'}).text.strip()
    data = soup.find_all('span', {'class': 'market_commodity_orders_header_promote'})
    quantity = data[0].text.strip()
    price = data[1].text.strip()[4:]

    
    return [item_name, quantity, price]
