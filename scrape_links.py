# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "scrape_links.py"

import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import requests
import time
import sys

from include import scroll_to_end,\
                    is_not_empty_string;

def read_input_file(_filename: str):

    data = {}
    with open(_filename, 'r') as infile:
        lines = infile.read().split('\n')
        for line in lines:
            elements = line.split('\t')
            if (len(elements) > 1):
                data[elements[0]] = [elements[1],\
                                     elements[2]]
        infile.close()
    return data

def write_headers_to_file(_filename: str, 
                          headers):
    
    with open(_filename, "a+") as outfile:
        outfile.write(str(headers))
        outfile.write('\n')
    outfile.close()

def write_results_to_file(_filename: str, 
                          data: dict,
                          position: int):
    
    with open(_filename, "a+") as outfile:
        outfile.write(str(position))
        # Enumerate through the job_listings, writing
        # each one as a comma-separated line.
        for val in data.values():
            outfile.write(",{v}".format(v=val))
        outfile.write('\n')
    outfile.close()

if __name__ == "__main__":
    timeout_codes = [403,469]
    # An input file is used to query a list of locations here.
    input_filename = sys.argv[1]
    # And the resulting job listings are saved at output_filename/
    output_filename = sys.argv[2] 

    links = read_input_file(input_filename)

    service = Service("Documents/chromedriver.exe")
    driver = uc.Chrome(service=service, 
                       headless=True) 
    driver.implicitly_wait(4) # Set the time to wait between calls

    bad_requests_counter = 0
    # Begin outer for loop
    for idx,(title,data) in enumerate(links.items(),
                                      start = 1):
        
        href = data[0]
        location = data[1]
        response = requests.get(href)
        # Begin 'if 1' 
        if (response.status_code == 200):
            
            # Load progress indicator
            sys.stdout.write("{cur} / {end}\r"\
                .format(cur=idx, end=len(links) ) )
            sys.stdout.flush()

            driver.get(href) # Navigate to the link
            time.sleep(0.8) 
            
            scroll_to_end(driver,2) # To load all elements
        
            descriptor_map = {"Job Title" : title,
                              "Location" : location} # Initialize data with job title

            # Try to save the employer name as a value of company.
            try:
                descriptor_map["Company"] = driver.find_element(By.XPATH, \
                    "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a").text
            except:
                descriptor_map["Company"] = "Not applicable"

            # Find the single <ul> element holding main job descriptors
            descriptors = driver.find_element(By.XPATH,\
                "/html/body/main/section[1]/div/div/section[1]/div/ul")
            
            descriptor_list_items = descriptors\
                .find_elements(By.TAG_NAME,"li")
            # Begin inner while    
            while(len(descriptor_list_items) > 0):
                descriptor_key_value = {}

                descriptor = descriptor_list_items.pop()

                # Get header as key and <span> as value.
                key = descriptor.find_element(\
                    By.TAG_NAME, 'h3').text
                value = descriptor.find_element(\
                    By.TAG_NAME, 'span').text

                if (is_not_empty_string(key) and\
                    is_not_empty_string(value)):

                    descriptor_map[key] = value
            # End inner while
            if (len(descriptor_map) > 0):
                if (idx == 1): 
                    write_headers_to_file(output_filename,\
                                          descriptor_map.keys())
                write_results_to_file(output_filename,
                                      descriptor_map,
                                      idx-1)
            # End if
            time.sleep(0.5)

        # Request failed; output the status
        # code neatly, and then sleep for 15 seconds.
        else:
            bad_requests_counter += 1
            sys.stdout.write("\r\nStatus {code}! x{n}\r\n"\
                             .format(code=response.status_code,\
                                     n=bad_requests_counter))
            if (response.status_code in timeout_codes):
                sys.stdout.write("Sleeping for 10 seconds...")
                time.sleep(10)
                sys.stdout.flush()

                pass
            else: 
                continue
            # End inner else 1

    # End outer for loop
    driver.close()
    exit("Done!")