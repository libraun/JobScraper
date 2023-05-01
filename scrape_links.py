# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "include.py"

import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import requests
import time
import sys

from include import *

if __name__ == "__main__":
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    links = read_input_file(input_filename)

    service = Service("Documents/chromedriver.exe")
    driver = uc.Chrome(service=service, \
                       headless=True)
    driver.implicitly_wait(3)

    job_listings = []
    bad_requests_counter = 0
    # Begin outer for loop
    for idx,(title,href) in enumerate(links.items(),
                                      start = 1):
        response = requests.get(href)
        # Begin if 1
        if (requests.get(href).status_code == 200):

            stdout_then_flush("{} / {}".format(idx, len(links)))

            driver.get(href)
            time.sleep(0.5)
            get_scroll_height(driver)

            descriptor_map = {"Job Title" : title}
            try:
                company_name_elem = driver.find_element(By.XPATH, "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a")
                descriptor_map["Company"] = company_name_elem.text
            except:
                descriptor_map["Company"] = "Not applicable"

            descriptors = driver.find_element(By.XPATH,"/html/body/main/section[1]/div/div/section[1]/div/ul")
            descriptor_list_items = descriptors.find_elements(By.TAG_NAME,"li")
            # Begin inner while    
            while(len(descriptor_list_items) > 0):
                descriptor_key_value = {}

                descriptor = descriptor_list_items.pop()
            
                key = descriptor.find_element(By.TAG_NAME, 'h3').text
                value = descriptor.find_element(By.TAG_NAME, 'span').text

                if ((key != None) and (key != '')) and \
                    ((value != None) and (value != '')):
                    descriptor_map[key] = value
            # End inner while
            if (len(descriptor_map) > 0):
                job_listings.append(descriptor_map)
            time.sleep(0.5)
        else:
            bad_requests_counter += 1
            stdout_then_flush("\nStatus {code}! x{n}"\
                             .format(code = response.status_code,
                                     n = bad_requests_counter))
            # A prettier/more verbose sleep alert
            for i in range(10,0):
                stdout_then_flush("Sleeping for {} seconds...".format(i))
                time.sleep(1)
            pass
            # End inner else 1
    # End outer for loop
    driver.close()
    driver._ensure_close()
    
    keys = job_listings[0].keys()
    with open('out.csv', 'a') as outfile:
        outfile.write("{}\n".format(str(keys[0])))
        for idx, desc in enumerate(job_listings):
            outfile.write(str(idx))
            for key, val in desc.items():
                stdout_then_flush("{key},{val}"\
                                 .format(key=key,val=val))
                outfile.write(",{}".format(val))
            outfile.write('\n')
        outfile.close()