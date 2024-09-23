# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "main.py"
import undetected_chromedriver as uc 
import yaml

from selenium.webdriver.chrome.service import Service


from Scraper import Scraper



if __name__ == "__main__":

    with open("config.yaml", "rb") as fp:
        config = yaml.safe_load(fp)["main"]
        

    #service = Service()
    driver = uc.Chrome(headless=False, use_subprocess=True) 
    driver.implicitly_wait(1)
    

    sc = Scraper(driver)
        
    sc.scrape(
        output_path=config["output-filepath"],
        job_filter=config["job-title"],
        location_filter=config["job-location"])
