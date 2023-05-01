# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "include.py"
from selenium import webdriver

import time
import sys

def clean_search_token(token: str):
    return token.lower().replace(" ","-").replace(',',';')

def write_list_to_file(filename: str, data: list,mode='a'):
    with open(filename, mode) as outfile:
        for value in data:
            outfile.write('{}\n'.format(value))
        outfile.close()
        
def write_dict_to_file(filename: str, data: dict,mode='a'):
    with open(filename, mode) as outfile:
        for key, value in data.items():
            outfile.write('{key}\t{val}\n'\
                          .format(key=key, val=value)) 
        outfile.close()
    
def get_scroll_height(_driver: webdriver):
    last_height = _driver.execute_script("return document.body.scrollHeight")
    while(True):
        _driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(2)
        # Calculate new scroll height and compare with last scroll height
        new_height = _driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return last_height

def read_input_file(_filename: str):
    data = {}
    with open(_filename, 'r') as infile:
        lines = infile.read().split('\n')
        for line in lines:
            elements = line.split('\t')
            if (len(elements) > 1):
                data[elements[0]] = elements[1]
        infile.close()
    return data

def stdout_then_flush(message: str):
    sys.stdout.writelines('{}\r'.format(message))
    sys.stdout.flush()