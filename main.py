# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "main.py"
import undetected_chromedriver as uc 
from selenium.webdriver.chrome.service import Service

import subprocess
import sys, re

from Scraper import Scraper


def run_scrape_links(links):
    args = ["python", "scrape_links.py", 
            "o_links.txt", "out_done.csv"]
    subprocess.run(args=args,)

if __name__ == "__main__":

    service = Service("Documents/chromedriver.exe")
    driver = uc.Chrome(service=service,
                       headless=True) 
    driver.implicitly_wait(3.5)

    sc = Scraper(driver)
    sc.scrape_links_from_file(input_path="o_links.txt", 
                              output_path="o.csv")
