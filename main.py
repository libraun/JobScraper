# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "main.py"
import undetected_chromedriver as uc 
from selenium.webdriver.chrome.service import Service

import argparse

from Scraper import Scraper


parser = argparse.ArgumentParser(
    desc="This program scrapes a list of job titles and their relevant information from LinkedIn.")

parser.add_argument("-j", "--job-title", type=str, required=True,
                    help="The job title filter to apply to the LinkedIn search.")
parser.add_argument("-l", "--location", type=str, required=True,
                    help="The location filter to apply to the LinkedIn search.")

parser.add_argument("-p", "--driver-path", type=str, required=True,
                    help="The filepath pointing to a chromedriver.")

parser.add_argument("-b", "--build-links", action="store_true", required=False,
                    help="Specifies that the parser should build job information from specified input file.")

parser.add_argument("-o", "--output-filepath", type=str, required=True,
                    help="""If '--build-links' is disabled, then output_filepath is the list to write
                    target URLs to. Otherwise, it's the destination to store the data from the query.""")
parser.add_argument("-i", "--input-filepath", type=str, default=None, required=False,
                    help="The filepath containing a list of URLs to scrape.")

if __name__ == "__main__":

    args = parser.parse_args()

    job_title_filter: str = args.job_title
    job_location_filter: str = args.job_location

    driver_path: str = args.driver_path

    build_links: bool = args.build_links

    input_path: str = args.input_filepath
    output_path: str = args.output_filepath

    service = Service(driver_path)
    driver = uc.Chrome(service=service, headless=True) 

    driver.implicitly_wait(3.5)

    sc = Scraper(driver)
    
    if build_links:
        
        sc.scrape_navigation_page(output_path=output_path,
                                  query_filter_job=job_title_filter,
                                  query_filter_location=job_location_filter)
    
    elif input_filepath is not None:

        sc.scrape_links_from_file(input_path="o_links.txt", output_path="o.csv")
