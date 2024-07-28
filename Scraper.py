import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By

import logging

import requests
import time
import sys

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
    while(new_height != last_height):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(sleep_duration)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script(
            "return document.body.scrollHeight")
        last_height = new_height
    return last_height

def __write_result_to_file__(result: dict, 
                             output_path: str,
                             headers = False,
                             mode="a+"):
    with open(output_path, mode) as outfile:
        # Write headers if headers == True
        if headers: 
            outfile.write(','.join(result.keys()))
        # Write the column values
        outfile.writelines(','.join(result.values()))

_STATUS_ERR_MSG = "Status {code}! x{count}"
class Scraper:
     
    def __init__(self, chrome_driver: uc.Chrome, mode: str='a+',
                 nav_url: str="http://www.linkedin.com/jobs/{job}-jobs-{location}"):
        self.driver = chrome_driver
        
        self.timeout_codes = (403, 429)
        self.bad_request_count = 0

        self.mode = mode

        self.nav_url = nav_url

    def close_driver(self):
        self.driver.close()

    def scrape_navigation_page(self, output_path: str,
                               query_filter_job: str,
                               query_filter_location: str,
                               sleep_time = 0.5):
        # Format target_url to include job & location 
        target_nav_url = self.nav_url.format(job=query_filter_job, 
                                             location=query_filter_location)
        # Load the URL
        response = requests.get(target_nav_url)

        if response.status_code == 200:
            self.driver.get(target_nav_url)

            _scroll_to_end(sleep_time=sleep_time)
            try:
                search_results = self.driver.find_element(
                    By.XPATH, '/html/body/div[1]/div/main/section[2]/ul')
                url_elems = search_results.find_elements(
                    By.TAG_NAME, 'a')
            except: 
                return None
            output = dict()

            for url_elem in url_elems:
                try:
                    span = url_elem.find_element(By.CLASS_NAME, "sr-only").text
                    link = url_elem.get_property('href')

                    output[span] = link

                    self.__write_result_to_file__(span,
                                                  output_path=output_path)
                except:
                    continue
        response.close()

    # Given a filename, scrapes each URL in the file for 
    # LinkedIn 
    def scrape_links_from_file(self,
                               input_path: str,
                               output_path: str):
        headers = True
        for title, url, location in _get_line(input_path):

            response = requests.get(url)
            if response.status_code == 200:   
                
                result = {'title':title, 'location':location, 'href':url }

                self.driver.get(url=url)
                result = self.scrape_url(url)
                if (result != None):
                    self.__write_result_to_file__(result, output_path,
                                                  headers=headers)
                    if headers: 
                        headers = False
            else:
                # Write message to console and sleep
                self.__log_bad_request__(response.status_code)
                time.sleep(15)
            # Finally close the response
            response.close()

    # Scrapes a given URL, and returns result job field 
    # descriptors as a dict 
    def scrape_url(self, url: str):

        self.driver.get(url=url)
        self.__scroll_to_end__(1.25) # To load all elements
        result_map = {}
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
        item_elems = descriptors.find_elements(By.TAG_NAME,"li")

        for description in item_elems:
            # Get header as key and <span> as value.
            key = description.find_element(By.TAG_NAME, 'h3').text
            value = description.find_element(By.TAG_NAME, 'span').text
            # Add result to current row if values are good
            if key != '' and value != '':
                result_map[key] = value
        # Return the result map
        return result_map

    def __write_result_to_file__(self,
                                 result: dict, 
                                 output_path: str,
                                 headers = False):
        with open(output_path, self.mode) as outfile:
            # Write headers if headers == True
            if headers: 
                outfile.write(','.join(result.keys()))
            # Write the column values
            outfile.writelines(self.__list_to_row__(result.values()))

    
    def __log_bad_request__(self,
                            code: int):
        self.bad_request_count += 1
        msg = self.status_err.format(code = code, count = self.bad_request_count)

        logging.warn(msg)

