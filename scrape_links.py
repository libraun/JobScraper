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

from include import read_input_file,\
                    get_scroll_height,\
                    is_not_empty_string;

if __name__ == "__main__":
    # An input file is used to query a list of locations here.
    input_filename = sys.argv[1]
    # And the resulting job listings are saved at output_filename/
    output_filename = sys.argv[2] 

    links = read_input_file(input_filename)

    service = Service("Documents/chromedriver.exe")
    driver = uc.Chrome(service=service, 
                       headless=True) 
    driver.implicitly_wait(1.5) # Set the time to wait between calls

    job_listings = []
    bad_requests_counter = 0
    # Begin outer for loop
    for idx,(title,href) in enumerate(links.items(),
                                      start = 1):
        response = requests.get(href)
        # Begin if 
        if (response.status_code == 200):
            
            # Load progress indicator
            sys.stdout.write("{cur} / {end}\r"
                .format(cur=idx, end=len(links) ) )
            sys.stdout.flush()

            driver.get(href); time.sleep(0.5) # Navigate to the link
            get_scroll_height(driver) # To load all elements
        
            descriptor_map = {"Job Title" : title} # Initialize data with job title

            # Try to save the employer name as a value of company.
            try:
                company_name_elem = driver.find_element(By.XPATH, 
                    "/html/body/main/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a")
                descriptor_map["Company"] = company_name_elem.text
            except:
                descriptor_map["Company"] = "Not applicable"

            # Find the single <ul> element holding main job descriptors
            descriptors = driver.find_element(By.XPATH,
                "/html/body/main/section[1]/div/div/section[1]/div/ul")
            descriptor_list_items = descriptors\
                .find_elements(By.TAG_NAME,"li")
            # Begin inner while    
            while(len(descriptor_list_items) > 0):
                descriptor_key_value = {}

                descriptor = descriptor_list_items.pop()

                # Get header as key and <span> as value.
                key = descriptor.find_element(
                    By.TAG_NAME, 'h3').text
                value = descriptor.find_element(
                    By.TAG_NAME, 'span').text

                if (is_not_empty_string(key) and
                    is_not_empty_string(value)):

                    descriptor_map[key] = value
            # End inner while
            if (len(descriptor_map) > 0):
                job_listings.append(descriptor_map)
            time.sleep(0.5)
        # End if

        # Request failed; output the status
        # code neatly, and then sleep for 15 seconds.
        else:
            bad_requests_counter += 1
            sys.stdout.write("""\r\nStatus {code}! x{n}
                             \nSleeping for 10 seconds... \r\n"""\
                             .format(code=response.status_code,
                                     n=bad_requests_counter))
            if (response.status_code == 469 or 
                response.status_code == 403):

                time.sleep(10)
                sys.stdout.flush()
                
                pass
            else: 
                continue
            # End inner else 1
    # End outer for loop

    driver.close()
    driver._ensure_close()
    
    # Assign keys of first entry to headers
    keys = job_listings[0].keys()
    # Write output to file
    with open('out.csv', 'a+') as outfile:
        # Write the header to start
        outfile.write("{}\n".format( str(keys[0]) ) )
        # Enumerate through the job_listings, writing
        # each one as a comma-separated line.
        for idx, desc in enumerate(job_listings):

            outfile.write( str(idx) )
            for val in desc.values():
                outfile.write(",{v}".format(v=val))
            outfile.write('\n')

        # End for loop
        outfile.close()
    exit("Done!")