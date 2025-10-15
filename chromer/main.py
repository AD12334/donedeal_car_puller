import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import argparse
import os

def screenshot_listings(driver, container_class, output_folder="screenshots", scroll_pause=0.01, scroll_step=50):
    """
    Scrolls the page slowly and takes screenshots of all containers matching container_class.
    """
    os.makedirs(output_folder, exist_ok=True)

    seen_elements = set()
    idx = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(0, last_height, scroll_step):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(scroll_pause)

        containers = driver.find_elements(By.CSS_SELECTOR, container_class)
        for container in containers:
            if id(container) not in seen_elements:
                seen_elements.add(id(container))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", container)
                time.sleep(0.1)
                screenshot_path = os.path.join(output_folder, f"container_{idx}.png")
                container.screenshot(screenshot_path)
                print(f"Saved {screenshot_path}")
                idx += 1
        if i <= last_height - 10:
            break

if __name__ == "__main__":
    # ----------------------------
    # CLI arguments
    # ----------------------------
    parser = argparse.ArgumentParser(description="Donedeal car search scraper")
    parser.add_argument("--price_from", type=int, default=5000, help="Minimum price")
    parser.add_argument("--price_to", type=int, default=8000, help="Maximum price")
    parser.add_argument("--year_from", type=int, default=2012, help="Earliest year")
    parser.add_argument("--sellerType", type=str, default="pro", help="Type of seller")
    parser.add_argument("--area", type=str, default="Clare", help="Area or location")
    args = parser.parse_args()

    arguments = [args.price_from, args.price_to, args.year_from, args.sellerType, args.area]

    # ----------------------------
    # Selenium setup
    # ----------------------------
    DRIVER_PATH = r"C:\Users\downe\chrome_driver\chromedriver-win64\chromedriver.exe"
    service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # ----------------------------
    # Navigate to Donedeal search URL
    # ----------------------------
    url = f'https://www.donedeal.ie/cars?price_from={arguments[0]}&price_to={arguments[1]}&year_from={arguments[2]}&sellerType={arguments[3]}&area={arguments[4]}'
    driver.get(url)
    ## next button = .GhostButton__SGhostButton-sc-1uq3hiv-0 dXRRVP Pagination__NavigationGhostButton-sc-1w9pc29-3.kOCgwa

    # ----------------------------
    # Accept cookies popup if present
    # ----------------------------
    try:
        cookie_btn = driver.find_element(By.ID, "didomi-notice-agree-button")
        cookie_btn.click()
    except Exception:
        pass
    cars = []
    # ----------------------------
    # Screenshot all listing containers
    # ----------------------------
    ###pictures and full car description -> .Cardstyled__Container-sc-ii4k9n-0.bFOEne
    #### car name  -> .LineClampstyled__Container-sc-1mg7xqt-0.kZaNUJ.SearchCardstyled__Title-sc-7ibu2h-6.igUdmi
    ### year,engine_size,mileage,time posted,location -> .SearchCardstyled__MetaInfoItem-sc-7ibu2h-8.jFdZDo
    container_class = ".SearchCardstyled__MetaInfoItem-sc-7ibu2h-8.jFdZDo"
    screenshot_listings(driver, container_class)
 ##TODO IMPLEMENT FILTERING FOR INDIVIDUAL COMPONENTS 
 ##for each container
 ## find the mileage, engine size, year etc
 ##find the price etc.
##store in a dict or a class instance

class Car:
    def __init__(self, name, year, engine_size, mileage, price, location, time_posted, link):
        self.name = name
        self.year = year
        self.engine_size = engine_size
        self.mileage = mileage
        self.price = price
        self.location = location
        self.time_posted = time_posted
        self.link = link

    def __repr__(self):
        return f"{self.year} {self.name}, {self.engine_size}, {self.mileage}, {self.price}, {self.location}, {self.time_posted}, {self.link}"

def create_email_content(cars):
    email_content = "Here are the car listings:\n\n"
    for car in cars:
        email_content += f"{car}\n"
    return email_content

def send_email(subject, body, to_email):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

def get_href(car_name):
    base_url = "https://www.donedeal.ie/cars-for-sale/"
    description = car_name.lower().replace(" ", "-")
    href = f"{base_url}{description}/"
    return href