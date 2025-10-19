import os
import re
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
        return (
            f"{self.year} {self.name}, {self.engine_size}, {self.mileage}, "
            f"{self.price}, {self.location}, {self.time_posted}, {self.link}"
        )


def extract_car_info(container, driver):
    try:
        title = container.find_element(By.CSS_SELECTOR, ".LineClampstyled__Container-sc-1mg7xqt-0.kZaNUJ.SearchCardstyled__Title-sc-7ibu2h-6.igUdmi").text
        price = container.find_element(By.CSS_SELECTOR, "[class*='Price']").text
        metadata = container.find_elements(By.CSS_SELECTOR, "[class*='MetaInfoItem']")
        url = container.find_element(By.TAG_NAME, "a").get_attribute("href")
        year = metadata[0].text if len(metadata) > 0 else ""
        engine_size = metadata[1].text if len(metadata) > 1 else ""
        mileage = metadata[2].text if len(metadata) > 2 else ""
        location = metadata[3].text if len(metadata) > 3 else ""
        time_posted = metadata[4].text if len(metadata) > 4 else ""
        title = process_car_title(title)
        if title == "invalid":
            return None
        mileage = process_mileage(mileage)
        
        # Create screenshots directory if it doesn't exist
        screenshots_dir = "car_screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        # Generate a unique filename based on the URL
        filename = url.split('/')[-1]
        if not filename:  # If URL ends with /, use the second to last part
            filename = url.split('/')[-2]
        screenshot_path = os.path.join(screenshots_dir, f"{filename}.png")
        
        # Take screenshot of the container
        container.screenshot(screenshot_path)
        
        return Car(title, year, engine_size, mileage, price, location, time_posted, url)

    except Exception as e:
        print(f"Error extracting car info: {e}")
        return None

    except Exception as e:
        return None


def scroll_and_extract(driver, container_selector):
    cars = []
    seen = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
        for c in containers:
            cid = c.id
            if cid in seen:
                continue
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
            time.sleep(0.2)
            car = extract_car_info(c, driver)
            if car:
                if("cars you may like" in car.name.lower()):
                    continue
                cars.append(car)
            seen.add(cid)

        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return cars
def check_duplicates(filename="cars.csv"):
    seen_links = set()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                parts = line.strip().split(",")
                if len(parts) >= 7:
                    link = parts[6]
                    seen_links.add(link)
    except Exception as e:
        print(f"[WARNING] Error checking duplicates: {e}")
    return seen_links

def write_to_csv(cars, seen_links, filename="cars.csv"):
    # Main CSV header
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("year,name,engine_size,mileage(km),price(eur),link\n")

    for car in cars:
        if car.link not in seen_links:
            # Clean price
            price = re.match(r"(\d+)", car.price.replace("€", "").replace(",", "").strip())
            clean_price = price.group(1) if price else ""

            # Write to main CSV
            with open(filename, "a", encoding="utf-8") as f:
                f.write(f"{car.year},{car.name},{car.engine_size},{car.mileage},{clean_price},{car.link}\n")

            # Write to brand CSV
            brand = car.name.split(" ")[0]
            if brand.lower() == "vw":
                brand = "Volkswagen"
            brand_file_path = f"{brand}_cars.csv"
            if not os.path.exists(brand_file_path):
                with open(brand_file_path, "w", encoding="utf-8") as bf:
                    bf.write("year,name,engine_size,mileage(km),price(eur),link\n")
            with open(brand_file_path, "a", encoding="utf-8") as bf:
                bf.write(f"{car.year},{car.name},{car.engine_size},{car.mileage},{clean_price},{car.link}\n")

def prepare_email(cars):
    lines = []
    for car in cars:
        if car.year in car.name:
            car.name = car.name.replace(car.year, "").strip()
        lines.append(f"{car.year},{car.name},{car.engine_size},{car.mileage},{car.location} - {car.price}\n{car.link}\n")
    return "\n".join(lines)

def send_email(subject, body, to_email):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    import glob
    import os

    from_email = "<your_email@gmail.com>"
    password = "<your_email_password>"

    # Create the container email message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Add the text part
    text_part = MIMEText(body)
    msg.attach(text_part)

    # Add all screenshots from the car_screenshots directory
    screenshots_dir = "car_screenshots"
    if os.path.exists(screenshots_dir):
        for img_path in glob.glob(os.path.join(screenshots_dir, "*.png")):
            try:
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data)
                    # Use the filename as Content-ID
                    img_name = os.path.basename(img_path)
                    image.add_header('Content-ID', f'<{img_name}>')
                    image.add_header('Content-Disposition', 'inline', filename=img_name)
                    msg.attach(image)
            except Exception as e:
                print(f"Error attaching image {img_path}: {e}")

    # Send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.send_message(msg)
        
    # Clean up screenshots after sending
    if os.path.exists(screenshots_dir):
        for file in os.listdir(screenshots_dir):
            file_path = os.path.join(screenshots_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

def process_car_title(title):
    car_brands = [
    "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "Hyundai", "Kia",
    "Volkswagen", "Subaru", "Mazda", "Mitsubishi", "Suzuki", "Renault",
    "Peugeot", "Fiat", "Dacia", "Skoda", "Citroen", "Vauxhall", "Opel",
    "Isuzu", "VW",
    "BMW", "Mercedes-Benz", "Audi", "Lexus", "Jaguar", "Volvo",
    "Land Rover", "Polestar",
    "Tesla", "Rivian", "Lucid", "NIO", "BYD", "MG", "Cupra", "Maxus", "XEV", "Skywell",
    "Ferrari", "Lamborghini", "Maserati", "Aston Martin",
    "Rolls-Royce", "Bentley", "Porsche",
    "Mini", "Seat", "Daihatsu", "Smart", "Triumph",
    "DS Automobiles", "Alfa Romeo", "Zapp", "SsangYong",
    "Jeep", "Hummer",
    "Infiniti"
]

    car_models = {
    "Toyota": [
        "Corolla", "Camry", "RAV4", "Hilux", "Yaris", "Prius", "Avensis", "Aygo",
        "Verso-S", "Aqua", "Vitz", "Passo", "IQ", "Aurist", "C-HR", "Auris",
        "bZ4X", "Alphard", "Voxy", "Land Cruiser", "C-HR Hybrid", "Auris Hybrid",
        "Sienta", "Crown", "Estima", "Dyna", "C-HR G Hybrid", "C-HR 1.8 Petrol Hybrid Automatic",
        "C-HR HYBRID SPORT", "C-HR PHEV SPORT", "Crolla", "CH-R G Hybrid", "C-HR HYBRID SPORT 4DR AUTO",
        "Verso 1.6 D-4D Aura 7 Seater", "Verso 2.0 D-4D TR 5DR 125BHP",
        "Highlander Highlander Sol 7 Seater AWD Top"
    ],
    "Honda": [
        "Civic", "Accord", "CR-V", "Jazz", "HR-V", "Pilot", "Fit", "Insight", "CRZ",
        "Shuttle", "Vezel", "Freed", "Grace", "Jade", "Vesel", "Vezel RS EDITION", "Vesel"
    ],
    "Ford": [
        "Focus", "Fiesta", "Mondeo", "Kuga", "Mustang", "Explorer", "EcoSport", "B-Max",
        "Tourneo Connect", "C-Max", "Galaxy", "S-Max", "Ka", "Puma", "Transit", "Tourneo Custom",
        "S-Max 1.6 TDCI Zetec S/S", "Transit Courier", "Puma ST-LINE",
        "C MAX ACTIVE 1.6 TDCI 95PS MY11 4"
    ],
    "Chevrolet": ["Cruze", "Malibu", "Camaro", "Equinox", "Trailblazer"],
    "Nissan": ["Altima", "Qashqai", "Leaf", "Juke", "Micra", "X-Trail", "Note", "Pulsar",
               "March", "Ariya", "Primastar", "Serena 2017"],
    "Hyundai": ["i10", "i20", "i30", "Tucson", "Kona", "Santa Fe", "ix35", "i40", "Aqua",
                "Ioniq", "INSTER Elegance", "ix20", "Bayon EXECUTIVE", "Bayon EXECUTIVE", "INSTER"],
    "Kia": ["Rio", "Ceed", "Sportage", "Sorento", "Stonic", "Niro", "Optima", "Venga",
            "Carens", "EV6", "EV3", "EV9", "EV6 Earth", "EV3 GT Line", "Picanto", "Soul",
            "EV4 EARTH 3 HATCHBACK", "EV4 EARTH 3 HATCHBACK"],
    "Volkswagen": [
        "Golf", "Passat", "Polo", "Tiguan", "Touareg", "Arteon", "Up", "CC",
        "Beetle", "Touran", "Jetta", "Sharan", "T-Roc", "Taigo", "California",
        "ID.3", "ID.4", "ID.5", "Caddy", "Taigo Style", "Golf GTI Clubsport",
        "Golf GTI Adidas Edition", "Golf TSI Highline", "T-Cross", "Passat GTE",
        "T-Roc R-line", "Taigo edition 75", "T-Roc 75 Edition 1.0tsi", "Golf R", "Touran",
        "ID.4 PRO LIFE", "ID.4 life DX", "T-Cross edition 75", "T-Roc Edition 75", "T-Roc R-line", "Taigo edition 75", "T-Cross T-cross Life", "T-Roc 1.0 TSI 110HP R-line",
        "CC 2.0 TDI COUPE"
    ],
    "VW": [
        "Golf", "Passat", "Polo", "Tiguan", "Touareg", "Arteon", "Up", "CC",
        "Beetle", "Touran", "Jetta", "Sharan", "T-Roc", "Taigo", "California",
        "ID.3", "ID.4", "ID.5", "Caddy", "Taigo Style", "Golf GTI Clubsport",
        "Golf GTI Adidas Edition", "Golf TSI Highline", "T-Cross", "Passat GTE",
        "T-Roc R-line", "Taigo edition 75", "T-Roc 75 Edition 1.0tsi", "Golf R", "Touran",
        "ID.4 PRO LIFE", "ID.4 life DX", "T-Cross edition 75", "Polo", "Golf R", "T-Roc"
    ],
    "Subaru": ["Impreza", "Forester", "Outback", "XV", "Legacy"],
    "Mazda": ["Mazda2", "Mazda3", "Mazda6", "CX-3", "CX-5", "CX-30", "Demio", "MX-5",
              "6 Commercial", "MPS", "CX-80 2 5L E Skyactiv Phev 327ps TAKUMI PLUS", "CX-80 2 5L E Skyactiv Phev 327ps TAKUMI PLUS", "6 GT", "Mazda 6",
              "CX-5 4x4", "CX-5 1.5k 16"]
    ,
    "Renault": [
        "Clio", "Megane", "Captur", "Kadjar", "Talisman", "Zoe", "Scenic",
        "Twingo", "Kangoo", "Arkana", "Fluence", "Austral", "Trafic",
        "Arkana R.s. Line E-tech Hybrid 145 Auto", "Arkana S Edition E-tech Hybrid 145 Auto",
        "Arkana Techno E-tech Hybrid 145 Auto", "Arkana TCe 140 Auto Techno",
        "5 E-Tech", "Symbioz 2025", "Rafale E-tech Hybrid 200 Esprit Alpine +", "5 E-Tech Iconic 52kWh 150hp",
        "Captur"
    ],
    "Citroen": ["C1", "C3", "C4", "C5 Aircross", "Berlingo", "DS3", "DS4", "Multi Space",
                "DS5", "Picasso", "Cactus Blue", "Grand Picasso", "Dispatch", "C3 AIRCROSS FEEL",
                "DS 3 2011 Diesel New Nct", "DS 3 2018 Diesel"],
    "Vauxhall": ["Corsa", "Astra", "Insignia", "Mokka", "Grandland", "Crossland", "Zafira",
                 "Meriva", "Karl", "Frontera", "Combo ENERGY CDTI S/S", "Combo 2000 SPORTIVE TD",
                 "Combo 2000 EDITION"],
    "Mercedes-Benz": [
        "A-Class", "B-Class", "C-Class", "E-Class", "GLA", "GLB", "GLC", "GLE",
        "S-Class", "EQC", "EQE", "EQV", "EQS", "V-Class", "CLA", "SL-Class",
        "CLE", "AMG", "E200 D AMG", "C220 Series D AMG", "EQA 250 AMG", "C300 AMG","C200",
        "EQE 300 Sport Edition", "EQE SUV EQE 300 SUV AMG Line advan", "CLA 250E AMG LINE PREMIUM",
        "EQB 250+ SPORT EXECUTIVE", "GLC 300 4matic", "GLC 300E AMG LINE", "E350CDI Estate 7 Seater",
        "C220cdi Sport", "CLA CLA200d AMG-LINE PREMIUM PLUS AU", "E200 BLUETEC AVANTGARDE",
        "GLE 350 DE 4MATIC AMG LINE", "EQB 300 4matic", "CLA Cla250 e Coupe AMG Line Premium",
        "CLE 300 e AMG Line Premium", "EQE 350 SPORT +", "C220cdi Sport", "E220 AMG LINE ESTATE",
        "E220 BLUETEC AVANTGARDE AUTO", "E220 AMG LINE", "E220", "B 180 STYLE 136HP 5DR",
        "GLC AMG-Line Automatic", "CLS 220 D AMG LINE", "E350CDI Estate",
        "A 1.5 CDI Sport", "SLK 2008 Automatic", "C220 SE 2.1 CDI", "A180 1.6 AMG Line Auto",
        "CLA Sport 2.1 CDI Auto", "A CLASS 2016 AMG LINE AUTO PANORAMIC ROOF"
    ],
    "Land Rover": [
        "Range Rover", "Discovery", "Freelander 2", "Evoque", "Defender", "Velar",
        "Discovery Sport 2.0D TD4 7 Seater", "Discovery Sport 2.0 TD4 AUTO SE",
        "Range Rover Evoque 2.0 eD4 SE 2wd", "Range Rover Evoque 2.0 TD4 SE Automatic"
    ],
    "SEAT": ["Ateca", "Leon", "Arona", "Ibiza", "Alhambra",
             "Toledo 1.2 TSI 86BHP S 4DR", "Tarraco FR TDI S-A DSG", "Mii 1.0 75hp Cosmopolitan 5D"],
    "Dacia": ["Duster", "Sandero", "Lodgy", "Dokker", "Spring", "Jogger", "Jogger TCe 110 Comfort",
              "Bigster 2025", "Bigster Journey HEV 155", "Duster",
              "Logan MCV SIGNATURE SCE 75 MY1 4DR STRAIGHT"],
    "Volvo": ["V50", "XC60", "EX30 Plus", "XC90", "S60", "S90", "V60", "V90",
              "V40 T4 AUTOMATIC 1.6 PETROL"],
    "Infiniti": ["Q30 2017"],
    "Hummer": ["H2", "H3"]
}

    for brand in car_brands:
        if brand.lower() in title.lower():
            models = car_models.get(brand, [])
            for model in models:
                if model.lower() in title.lower():
                    return f"{brand} {model}"
    #write to log for manual review
    with open("unmatched_titles.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"{title}\n")
    return "invalid"

def process_mileage(mileage_str):
    if "km" in mileage_str.lower():
        mileage_str = mileage_str.lower().replace("km", "").strip()
        mileage_str = mileage_str.replace(",", "")
        return mileage_str
    else:
        mileage_str = mileage_str.lower().replace("mi", "").strip()
        mileage_str = mileage_str.replace(",", "")
        mileage_str = str(int(float(mileage_str) * 1.60934))
        return mileage_str

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Donedeal car search scraper")
    # Price filters
    parser.add_argument("--price_from", type=int, help="Minimum price")
    parser.add_argument("--price_to", type=int, help="Maximum price")
    
    # Year filter
    parser.add_argument("--year_from", type=int, help="Earliest year")
    
    # Mileage filters
    parser.add_argument("--mileage_from", type=int, help="Minimum mileage in kilometers")
    parser.add_argument("--mileage_to", type=int, help="Maximum mileage in kilometers")
    
    # Car specific filters
    parser.add_argument("--brand", type=str, help="Single brand or comma-separated list of brands (e.g., 'Ford,Toyota,BMW')")
    parser.add_argument("--model", type=str, help="Car model (e.g., Fiesta, Corolla) - only used when a single brand is specified")
    
    # Other filters
    parser.add_argument("--sellerType", type=str, default="pro", help="Type of seller (private/pro)")
    parser.add_argument("--area", type=str, help="Single area or comma-separated list of areas (e.g., 'Clare,Dublin,Cork')")
    parser.add_argument("--email", type=str, default="", help="Email address to send results to")
    parser.add_argument("--no_params_mode", type=bool, default=False, help="Run without filters")
    
    args = parser.parse_args()

    service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    if args.no_params_mode:
        url = "https://www.donedeal.ie/cars"
    else:
        # Start with base URL
        url = "https://www.donedeal.ie/cars"
        if args.brand and args.model:
            url = f"https://www.donedeal.ie/cars/{args.brand}/{args.model}"
        elif args.brand:
            brands = [brand.strip() for brand in args.brand.split(",")]
            if len(brands) == 1:
                url = f"https://www.donedeal.ie/cars/{brands[0]}"
            
        # Add query parameters
        params = []
        
        if args.price_from:
            params.append(f"price_from={args.price_from}")
        if args.price_to:
            params.append(f"price_to={args.price_to}")
        if args.year_from:
            params.append(f"year_from={args.year_from}")
        if args.mileage_from:
            params.append(f"mileage_from={args.mileage_from}")
        if args.mileage_to:
            params.append(f"mileage_to={args.mileage_to}")
        if args.sellerType:
            params.append(f"sellerType={args.sellerType}")
        
        # Handle multiple brands if no specific model is given
        if args.brand and not args.model:
            brands = [brand.strip() for brand in args.brand.split(",")]
            if len(brands) > 1:
                for brand in brands:
                    params.append(f"section={brand}")
                    
        # Handle multiple areas
        if args.area:
            areas = [area.strip() for area in args.area.split(",")]
            for area in areas:
                params.append(f"area={area}")
            
        # Add parameters to URL if any exist
        if params:
            url += "?" + "&".join(params)
    driver.get(url)

    # Accept cookies if visible
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        ).click()
    except Exception:
        pass

    all_cars = []
    container_selector = "[class*='Listingsstyled__ListItem']"

    while True:
        # Extract cars from current page
        page_cars = scroll_and_extract(driver, container_selector)
        all_cars.extend(page_cars)

        try:
            next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='go-to-next-page']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(0.5)
            next_button.click()
            time.sleep(2)  # wait for the next page to load
        except Exception:
            print("[INFO] No more pages found.")
            break

    driver.quit()

    # Print or prepare email
    email_body = prepare_email(all_cars)
    send_email("Donedeal Car Search Results", email_body,"adamdownes22@gmail.com")
    print(email_body)
    print(f"\n[INFO] Total cars extracted: {len(all_cars)}\n")
    write_to_csv(all_cars, check_duplicates())
