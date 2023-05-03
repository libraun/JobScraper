from selenium import webdriver
import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import requests
import time
import sys

from include import clean_search_token, scroll_to_end

class Scraper:
     
    def __init__(self,
                 chrome_driver: webdriver.Chrome,
                 mode='a+'):
        self.driver = chrome_driver
        
        self.timeout_codes = [403,429]
        self.bad_request_count = 0

        self.mode = mode

        self.status_err = "Status {code}! x{count}"
        self.nav_url = "http://www.linkedin.com/jobs/{job}-jobs-{location}"

    def close_driver(self):
        self.driver.close()

    def __get_line__(self,
                     filename: str):
        with open(filename, 'r') as infile:
            lines = infile.read().split('\n')
        for line in lines:
            fields = line.split('\t')
            if len(fields) > 1:
                yield fields
    def scrape_navigation_page(self, 
                               output_path: str,
                               query_filter_job: str,
                               query_filter_location: str,
                               sleep_time = 0.5):
        target_url = self.nav_url.format(
            job=query_filter_job,
            location=query_filter_location)
        self.driver.get(target_url)
        time.sleep(1)
        self.__scroll_to_end__(
            sleep_time=sleep_time)
        try:
            search_result_list = self.driver.find_element(
                By.XPATH, '/html/body/div[1]/div/main/section[2]/ul')
            results = search_result_list.find_elements(
                By.TAG_NAME, 'a')
        except: 
            return None
        output = {}
        # Begin while
        while len(results) > 0:
            result = results.pop()
            try:
                span = result.find_element(By.CLASS_NAME, "sr-only").text
                link = result.get_property('href')

                output[span] = link
                self.__write_result_to_file__(span,
                                          output_path=output_path)
            except:
                continue
    def scrape_links_from_file(self,
                               input_path: str,
                               output_path: str):
        headers = True
        for sep_line in self.__get_line__(input_path):
            
            title = sep_line[0]
            url = sep_line[1]
            location = sep_line[2]

            response = requests.get(url)
            if (response.status_code == 200):   
                
                result = { 'title' : title,
                           'location' : location,
                           'href' : url }

                self.driver.get(url=url)
                result = self.scrape_url(url)
                if (result != None):
                    self.__write_result_to_file__(result,
                                                  output_path,
                                                  headers=headers)
                    if headers: 
                        headers = False
            else:
                # Write message to console and sleep if needed
                self.__log_bad_request__(response.status_code)
                if response.status_code in self.timeout_codes:
                    time.sleep(15)
                    pass
                # Likely code 500; continue to next URL.
                continue
            # Finally close the response
            response.close()

    def __scroll_to_end__(self,
                          sleep_time):
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")
        while(True):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(sleep_time)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        return last_height

    def scrape_url(self, url: str):
        self.driver.get(url=url)
        time.sleep(1)
        self.__scroll_to_end__(1.5) # To load all elements
        result_map = {}
        # Try to save the employer name as a value of company.
        try:
            result_map["Company"] = self.driver.find_element(By.XPATH, \
              "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a").text
        except: 
            result_map["Company"] = "Not applicable"
        try:
            descriptors = self.driver.find_element(By.XPATH,\
                "/html/body/main/section[1]/div/div/section[1]/div/ul")
        except: 
            return None
        item_elems = descriptors.find_elements(By.TAG_NAME,"li")
        # Begin inner while    
        while len(item_elems) > 0:
            desc = item_elems.pop()
            # Get header as key and <span> as value.
            key = desc.find_element(By.TAG_NAME, 'h3').text
            value = desc.find_element(By.TAG_NAME, 'span').text

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
                outfile.write(','.join([key for key in result.keys()]))
            # Write a new line
            outfile.write('\n')
            # Write the column values
            outfile.write(','.join([value for value in result.values()]))

    def __log_bad_request__(self,
                            code: int):
        self.bad_request_count += 1
        msg = self.status_err.format(
            code = code,
            count = self.bad_request_count)
        self.__write_then_flush__(msg)

    def __write_then_flush__(self, 
                             text : str):
        sys.stdout.write("\r\n{}\r\n".format(text))
        sys.stdout.flush()

    