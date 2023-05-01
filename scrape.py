# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "include.py"

import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import sys

from include import *

if __name__ == "__main__":
    output_filename = sys.argv[1]
    search_token = clean_search_token(sys.argv[2])
    search_location = clean_search_token(sys.argv[3])

    url = "http://www.linkedin.com/jobs/{voc}-jobs-{loc}"\
            .format(voc=search_token, loc=search_location)

    service = Service("/Documents/chromedriver.exe")
    driver = uc.Chrome(service=service,headless=True)
    
    driver.implicitly_wait(3)
    driver.get(url=url)

    height = get_scroll_height(driver)

    search_result_list = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/section[2]/ul')
    results = search_result_list.find_elements(By.TAG_NAME, 'a')

    output = {}
    result_len = len(results)
    idx = 0
    # Begin while
    while len(results) > 0:
        idx += 1
        stdout_then_flush("{} / {}".format(idx, result_len))

        result = results.pop()
        try:
            span = result.find_element(By.CLASS_NAME, "sr-only").text
            link = result.get_property('href')

            output[span] = link
        except:
            continue
        output[span] = link
    # End while
    driver.close()
    driver._ensure_close()

    write_dict_to_file(output_filename,output,mode='a')