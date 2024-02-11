import time
import random
from data_collecter import Collector

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


from selenium import webdriver
from selenium.common import exceptions as se
from selenium.webdriver.chrome.service import Service

CHROME_DRIVER = Service("/home/qiwi/chromedriver-linux64/chromedriver")

class ParallelDriverManager():
    def __init__(self, threads=1):
        self.threads = threads

        self.drivers = {thread_num: self.start_driver() for thread_num in range(threads)}
        self.url_pool = []

    #index driver list
    def __getitem__(self, driver_num):
        return self.drivers.get(driver_num)
    
    #set driver
    def __setitem__(self, driver_num, driver):
        self[driver_num] = driver

    def start_driver(self):
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-javascript")
        driver = webdriver.Chrome(service=CHROME_DRIVER, options=chrome_options)
        return driver

    # stop all drivers, clear list
    def stop_driver(self, index):
        self[index].quit()
        self[index] = None

    #set urls
    def set_urls(self, urls):
        self.url_pool = urls

    #start parrallel url_tasks
    def parallel_url_task(self, method, *args):
        parallel_collector = Collector()

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for driver in self.drivers:
                future = executor.submit(self.url_task, method, driver, *args)
                futures.append(future)

        #submit collector object to the parallel collector
        for future in concurrent.futures.as_completed(futures):
            collector = future.result()
            parallel_collector += collector

        return parallel_collector.get_data()

    def url_task(self, method, driver, *args):
        #init data collector
        collector = Collector()

        #iterate over url pool, call method, return output if any
        while self.url_pool:
            #iterate over url pool
            url = self.url_pool.pop(0)
            driver.get(url)

            #call method on driver, once the url is loaded
            thread_out = method(driver, *args)

            #append data to collector
            collector += thread_out

        #return collector
        return collector
    
    # scroll, used to trigger javascript load on pages like reddit, x (twitter)
    @staticmethod
    def scroll_entire_page(driver, timeout):
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        scrolls_done = 0
        while scrolls_done < timeout:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            # Adjust the waiting time based on your network speed
            time.sleep(random.randint(200, 300)/100)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls_done += 1

        return False