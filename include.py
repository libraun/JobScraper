# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "include.py"
import undetected_chromedriver as uc

import time

def is_not_empty_string(text: str):
    if ((text != None) and (text != '')):
        return True
    return False

def close_driver(_driver: uc.Chrome):
    _driver.close()
    _driver._ensure_close()

def clean_search_token(token: str):
    return token.lower().replace(" ","-").replace(',',';')

def write_list_to_file(filename: str, data: list,mode='a+'):
    with open(filename, mode) as outfile:
        for value in data:
            outfile.write('{}\n'.format(value))
        outfile.close()
        
def write_dict_to_file(filename: str, data: dict,mode='a+'):
    with open(filename, mode) as outfile:
        for key, value in data.items():
            outfile.write('{key}\t{val}\n'\
                          .format(key=key, 
                                  val=value)) 
        outfile.close()
    
def scroll_to_end(_driver: uc.Chrome, sleep_duration: int):
    last_height = _driver.execute_script(
        "return document.body.scrollHeight")
    while(True):
        _driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(sleep_duration)
        # Calculate new scroll height and compare with last scroll height
        new_height = _driver.execute_script(
            "return document.body.scrollHeight")
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