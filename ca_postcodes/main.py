import os
import re
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')  # Path to chromedriver.exe
CONN = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Database connection and pagination
def get_addresses_from_db(limit=1000, offset=0):    
    cur = CONN.cursor()
    cur.execute(
            f"""
                SELECT DISTINCT 
                concat(
                    street_no, 
                    ' ', 
                    street_full_name, ', ', city, ', ', 
                    CASE 
                        WHEN region = 'Alberta' THEN 'AB'
                        WHEN region = 'British Columbia' THEN 'BC'
                        WHEN region = 'Manitoba' THEN 'MB'
                        WHEN region = 'New Brunswick' THEN 'NB'
                        WHEN region = 'Northwest Territories' THEN 'NT'
                        WHEN region = 'Nova Scotia' THEN 'NS'
                        WHEN region = 'Ontario' THEN 'ON'
                        WHEN region = 'Prince Edward Island' THEN 'PE'
                        WHEN region = 'Quebec' THEN 'QC'
                        WHEN region = 'Saskatchewan' THEN 'SK'
                        WHEN region = 'Newfoundland and Labrador' THEN 'NL'
                        WHEN region = 'Yukon' THEN 'YT'
                        WHEN region = 'Nunavut' THEN 'NU'
                        ELSE region
                    END
                ) as address, 
                street_no, 
                street_full_name, 
                concat (street_no, ' ', street_full_name) as full_address,
            concat (city, ', ', 
                CASE 
                    WHEN region = 'Alberta' THEN 'AB'
                    WHEN region = 'British Columbia' THEN 'BC'
                    WHEN region = 'Manitoba' THEN 'MB'
                    WHEN region = 'New Brunswick' THEN 'NB'
                    WHEN region = 'Northwest Territories' THEN 'NT'
                    WHEN region = 'Nova Scotia' THEN 'NS'
                    WHEN region = 'Ontario' THEN 'ON'
                    WHEN region = 'Prince Edward Island' THEN 'PE'
                    WHEN region = 'Quebec' THEN 'QC'
                    WHEN region = 'Saskatchewan' THEN 'SK'
                    WHEN region = 'Newfoundland and Labrador' THEN 'NL'
                    WHEN region = 'Yukon' THEN 'YT'
                    WHEN region = 'Nunavut' THEN 'NU'
                    ELSE region
                END,
             ', ') as city_region,
            city, 
            region
        FROM public.mrag_ca_addresses
        WHERE postal_code IS NULL AND region = 'Alberta' AND city = 'Calgary'
        LIMIT {limit} OFFSET {offset}
    """)
    addresses = cur.fetchall()
    cur.close()
    return addresses

def update_postal_code_in_db(street_no, street_full_name, city, region, postal_code):
    cur = CONN.cursor()
    cur.execute("""
        UPDATE public.mrag_ca_addresses 
        SET postal_code = %s 
        WHERE street_no = %s 
          AND street_full_name = %s 
          AND city = %s 
          AND region = %s
    """, (postal_code, street_no, street_full_name, city, region))
    CONN.commit()
    cur.close()

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    # options.headless = True
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def expand_address_abbreviations(address):
    replacements = {
        r"\sAC\s": r" Acres ",
        r"\sAL\s": r" Alley ",
        r"\sAV\s": r" Ave ",
        r"\sBA\s": r" Bay ",
        r"\sBE\s": r" Beach ",
        r"\sBN\s": r" Bend ",
        r"\sBV\s": r" Blvd ",
        r"\sCA\s": r" Cape ",
        r"\sCE\s": r" Ctr ",
        r"\sCI\s": r" Cir ",
        r"\sCL\s": r" Close ",
        r"\sCM\s": r" Common ",
        r"\sCO\s": r" Crt ",
        r"\sCR\s": r" Cres ",
        r"\sCV\s": r" Cove ",
        r"\sDI\s": r" Divers ",
        r"\sDO\s": r" Downs ",
        r"\sDR\s": r" Dr ",
        r"\sEN\s": r" End ",
        r"\sES\s": r" Estate ",
        r"\sFR\s": r" Fwy ",
        r"\sGA\s": r" Gate ",
        r"\sGT\s": r" Gate ",
        r"\sGD\s": r" Gdns ",
        r"\sGL\s": r" Glen ",
        r"\sGR\s": r" Green ",
        r"\sGV\s": r" Grove ",
        r"\sHB\s": r" Harbr ",
        r"\sHE\s": r" Heath ",
        r"\sHI\s": r" Hwy ",
        r"\sHL\s": r" Hill ",
        r"\sHO\s": r" Hollow ",
        r"\sHT\s": r" Hts ",
        r"\sIN\s": r" Inlet ",
        r"\sIS\s": r" Island ",
        r"\sKN\s": r" Knoll ",
        r"\sKY\s": r" Key ",
        r"\sLD\s": r" Landng ",
        r"\sLI\s": r" Link ",
        r"\sLN\s": r" Lane ",
        r"\sLO\s": r" Loop ",
        r"\sMA\s": r" Mall ",
        r"\sMD\s": r" Meadow ",
        r"\sME\s": r" Mews ",
        r"\sMR\s": r" Manor ",
        r"\sMT\s": r" Mount ",
        r"\sMZ\s": r" Maze ",
        r"\sPA\s": r" Pk ",
        r"\sPH\s": r" Path ",
        r"\sPK\s": r" Pky ",
        r"\sPL\s": r" Pl ",
        r"\sPM\s": r" Prom ",
        r"\sPR\s": r" Parade ",
        r"\sPS\s": r" Pass ",
        r"\sPZ\s": r" Plaza ",
        r"\sQY\s": r" Quay ",
        r"\sRD\s": r" Rd ",
        r"\sRG\s": r" Ridge ",
        r"\sRI\s": r" Rise ",
        r"\sRO\s": r" Row ",
        r"\sRU\s": r" Run ",
        r"\sST\s": r" St ",
        r"\sTC\s": r" Terr ",
        r"\sTR\s": r" Trail ",
        r"\sVA\s": r" Vale ",
        r"\sVG\s": r" Villge ",
        r"\sVI\s": r" Villas ",
        r"\sVS\s": r" Vista ",
        r"\sVW\s": r" View ",
        r"\sWD\s": r" Wynd ",
        r"\sWK\s": r" Walk ",
        r"\sWO\s": r" Wood ",
        r"\sWY\s": r" Way ",
        r"\sXS\s": r" Cross "
    }

    for abbrev, full in replacements.items():
        address = re.sub(abbrev, full, address)
    return address

def get_postal_code(driver, address, full_address, street_full_name, city_region):
    target_url = "https://www.canadapost-postescanada.ca/ac/"

    # Check if the page is already loaded
    if driver.current_url != target_url:
        driver.get(target_url)
        time.sleep(3)  # Allow time for the page to load
        
    # Expand abbreviations in the address
    address = expand_address_abbreviations(address)
    full_address = expand_address_abbreviations(full_address)    
    street_full_name = expand_address_abbreviations(street_full_name)
    
    search_box = driver.find_element(By.CSS_SELECTOR, "#address-search")
    search_box.clear()
    driver.execute_script("arguments[0].value = arguments[1];", search_box, address)
    search_box.send_keys(Keys.SPACE);    
    time.sleep(3)  # Allow time for the dropdown to populate
    
    try:
        # Wait until the parent element is present
        parent_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#top > div.pca > div:nth-child(1) > div.pca.pcalist"))
        )

        # Find all .pcaitem elements within the parent element
        items = parent_element.find_elements(By.CSS_SELECTOR, ".pcaitem")
        full_address = full_address.strip().lower()
        for item in items:
            title = item.get_attribute("title").strip().lower()
            # Check if the title matches the full address and the description starts with the city_region            
            if full_address in title or title == street_full_name.strip().lower():
                description = item.find_element(By.CSS_SELECTOR, ".pcadescription").text
                if city_region in description:
                    pattern = f"^.*{re.escape(city_region)}"
                    description = re.sub(pattern, "", description).strip()
                    # Regex pattern to match the postal code format at the end of the string
                    match = re.search(r"^(\w{3}\s\w{3})\s*", description)
                    if match:
                        postal_code = match.group(0)
                        return postal_code
    except Exception as e:
        print(f"Error fetching postal code for {address}: {e}")
        return None

    return None  # Return None if no postal code is found

if __name__ == "__main__":
    driver = create_driver()
    limit = 1000
    offset = 0

    while True:
        addresses = get_addresses_from_db(limit, offset)
        if not addresses:
            break

        for address, street_no, street_full_name, full_address, city_region, city, region in addresses:
            print(f"Fetching postal code for: {address}")
            postal_code = get_postal_code(driver, address, full_address, street_full_name, city_region)
            if postal_code:
                print(f"Found postal code: {postal_code} for address: {address}")
                update_postal_code_in_db(street_no, street_full_name, city, region, postal_code)
            else:
                print(f"Could not find postal code for address: {address}")   
        offset += limit

    driver.quit()
