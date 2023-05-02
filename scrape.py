# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "scrape.py"

import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import sys

from include import clean_search_token, scroll_to_end

def write_dict_to_file(filename: str, 
                       data: dict,
                       location: str,
                       mode='a+'):
    
    with open(filename, mode) as outfile:
        for key, value in data.items():
            outfile.write('{key}\t{val}\t{location}\n'\
                          .format(key=key, \
                                  val=value, \
                                  location=location.replace('-',' '))) 
        outfile.close()

if __name__ == "__main__":
    output_filename = sys.argv[1]
    query_filter_job = sys.argv[2]
    query_filter_location = sys.argv[3]

    query_filter_job = clean_search_token(query_filter_job)
    query_filter_location = clean_search_token(query_filter_location)

    url = "http://www.linkedin.com/jobs/{job}-jobs-{location}"\
            .format(job = query_filter_job, 
                    location = query_filter_location)

    service = Service("/Documents/chromedriver.exe")
    driver = uc.Chrome(service = service,\
                       headless=True)
    
    driver.implicitly_wait(2)
    driver.get(url=url)

    height = scroll_to_end(driver,1)

    try:
        search_result_list = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/section[2]/ul')
        results = search_result_list.find_elements(By.TAG_NAME, 'a')
    except:
        exit()
    result_len = len(results)
    output = {}
    idx = 0
    # Begin while
    while len(results) > 0:
        result = results.pop()
        try:
            span = result.find_element(By.CLASS_NAME, "sr-only").text
            link = result.get_property('href')

            output[span] = link
        except:
            continue
        idx += 1
        sys.stdout.write("{} / {}\r".format(idx, result_len))
        sys.stdout.flush()
    # End while
    driver.close()
    write_dict_to_file(output_filename,\
                       output,\
                       query_filter_location,\
                       mode='a+')