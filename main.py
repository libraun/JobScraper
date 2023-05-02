# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "main.py"
import undetected_chromedriver as uc 
from selenium.webdriver.chrome.service import Service

import subprocess
import sys, re

def run_scrape_list():
    links = "o_links.txt"
    search_term = "software engineer"
    with open("partial_list.txt", 'r') as infile:
        cities = [line.lower() for line in\
                  infile.read().split('\n')]
        infile.close()
    for city in cities:
        re.sub("https","http", city)
        args = ["python", "scrape.py", \
                links, \
                search_term, city]
        subprocess.run(args=args)

def run_scrape_links(links):
    args = ["python", "scrape_links.py", 
            "o_links.txt", "out_done.csv"]
    subprocess.run(args=args,)

if __name__ == "__main__":
    operation_mode = int(sys.argv[1])
    assert operation_mode < 3 and operation_mode >= 0, \
        exit("ERROR: Enter 0 to scrape list, 1 to scrape links, 2 all")
    
    if (operation_mode == 0):
        print("Getting job postings from LinkedIn.com...")
        run_scrape_list()

    elif (operation_mode == 1):
        print("Getting data from job postings...")
        run_scrape_links("o_links.txt")

    elif (operation_mode == 2):
        print("Getting job postings from LinkedIn.com...")
        run_scrape_list()

        print("Getting data from job postings...")
        run_scrape_links("o_links.txt")

    exit("Done!")
    
    

