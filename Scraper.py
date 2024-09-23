import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By

import logging

import csv

import re
import time

from typing import Iterable

def _get_line(filename: str):
    with open(filename, 'r') as infile:
        lines = infile.readlines()
        for line in lines:
            yield line.split('\t')

def _scroll_to_end(driver: uc.Chrome, sleep_duration: float):
                          
    time.sleep(sleep_duration)
    
    last_height = driver.execute_script(
        "return document.body.scrollHeight")
    
    new_height = None
    while new_height != last_height:

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(sleep_duration)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script(
            "return document.body.scrollHeight")
        last_height = new_height
    return last_height

def _write_result_to_file(content: Iterable, output_path: str, sep: str=",", mode: str="a+"):

    with open(output_path, mode) as outfile:
        # Write headers if headers == True
        # Write the column values
        outfile.writelines(sep.join(content))

# Constants

_STATUS_ERR_MSG = "Status {code}! x{count}"
_MAIN_URL = "http://www.linkedin.com/jobs/{job}-jobs-{location}"

class Scraper:

    timeout_codes = (403, 429)
    bad_request_count = 0

    def __init__(self, chrome_driver: uc.Chrome, mode: str='a+'):

        self.driver = chrome_driver
        
        self.timeout_codes = (403, 429)

        self.mode = mode

    def scrape(self, output_path: str,
               job_filter: str, 
               location_filter: str):

        target_nav_url = _MAIN_URL.format(
            job=job_filter, location=location_filter)


        
        self.driver.get(target_nav_url)
        _scroll_to_end(self.driver, sleep_duration=1)
        time.sleep(1.5)
        while self.driver.current_url == "https://www.linkedin.com":
            self.driver.get(target_nav_url)
            time.sleep(1)

        self.driver.find_element(By.XPATH, "/html/body").click()
        

        _scroll_to_end(self.driver, sleep_duration=1)
        try:
            search_results = self.driver.find_element(
                By.XPATH, '/html/body/div[1]/div/main/section[2]/ul')
            
            url_elems = [elem for elem in 
                         search_results.find_elements(By.TAG_NAME, 'a')]
        except: 
            return False
        
        with open(output_path, "w+", newline="") as fp:
            writer = csv.writer(fp, delimiter=",")
            for url in url_elems:
                url.click()

                result = self.scrape_url(url)
            
                if result is not None:
                    print(result.values())
                    print(writer.writerow(result.values()))

    # Scrapes a given URL, and returns result job field 
    # descriptors as a dict 
    def scrape_url(self, url: str) -> dict:

        # Get URL, scroll to end to grab all information
    #    self.driver.get(url=url)
        _scroll_to_end(self.driver, 1)

        if re.search("authwall", self.driver.current_url):
            return None

        self.driver.find_element(By.XPATH, "/html/body").click()

        result_map = dict()
        # Try to save the employer name as a value of company.
        # There are probably better ways to do this...
        try:
            result_map["Company"] = self.driver.find_element(By.XPATH, \
              "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a").text
        except: 
            result_map["Company"] = "Not applicable"

        # Tries to find descriptor box and returns None if N/A
        try:
            descriptors = self.driver.find_element(By.XPATH,\
                "/html/body/main/section[1]/div/div/section[1]/div/ul")
        except: 
            return None
        
        for description in descriptors.find_elements(By.TAG_NAME,"li"):
            # Get header as key and <span> as value.
            key = description.find_element(By.TAG_NAME, 'h3').text
            value = description.find_element(By.TAG_NAME, 'span').text
            # Add result to current row if values are good
            if key != '' and value != '':
                result_map[key] = value
        # Return the result map
        return result_map

    
    def _log_bad_request(self, code: int):

        self.bad_request_count += 1
        msg = _STATUS_ERR_MSG.format(code = code, count = self.bad_request_count)

        logging.warning(msg)

