# housing_etl/scraping.py
import pandas as pd
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_edgeprop_properties():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # ← important
    options.add_argument('--no-sandbox')  # ← important for Docker
    options.add_argument('--disable-dev-shm-usage')  # ← use /tmp instead of /dev/shm
    options.add_argument('--disable-gpu')  # ← optional but safe
    options.add_argument('--remote-debugging-port=9222')  # ← useful for DevTools
    options.add_argument('--disable-extensions')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)

    
    districts = {
        "Raffles Place, Cecil, Marina, People's Park": 1024,
        "Anson, Tanjong Pagar": 1025,
        "Queenstown, Tiong Bahru": 1026,
        "Telok Blangah, Harbourfront": 1027,
        "Pasir Panjang, Hong Leong Garden, Clementi New Town": 1028,
        "High Street, Beach Road (part)": 1029,
        "Middle Road, Golden Mile": 1030,
        "Little India": 1031,
        "Orchard, Cairnhill, River Valley": 1032,
        "Ardmore, Bukit Timah, Holland Road, Tanglin": 1033,
        "Watten Estate, Novena, Thomson": 1034,
        "Balestier, Toa Payoh, Serangoon": 1035,
        "Macpherson, Braddell": 1036,
        "Geylang, Eunos": 1037,
        "Katong, Joo Chiat, Amber Road": 1038,
        "Bedok, Upper East Coast, Eastwood, Kew Drive": 1039,
        "Loyang, Changi": 1040,
        "Tampines, Pasir Ris": 1041,
        "Serangoon Garden, Hougang, Ponggol": 1042,
        "Bishan, Ang Mo Kio": 1043,
        "Upper Bukit Timah, Clementi Park, Ulu Pandan": 1044,
        "Jurong": 1045,
        "Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang": 1046,
        "Lim Chu Kang, Tengah": 1047,
        "Kranji, Woodgrove": 1048,
        "Upper Thomson, Springleaf": 1049,
        "Yishun, Sembawang": 1050,
        "Seletar": 1051
        }
    district_region = {
        "Raffles Place, Cecil, Marina, People's Park": "Central",
        "Anson, Tanjong Pagar": "Central",
        "Queenstown, Tiong Bahru": "Central",
        "Telok Blangah, Harbourfront": "Central",
        "High Street, Beach Road (part)": "Central",
        "Middle Road, Golden Mile": "Central",
        "Little India": "Central",
        "Orchard, Cairnhill, River Valley": "Central",
        "Ardmore, Bukit Timah, Holland Road, Tanglin": "Central",
        "Watten Estate, Novena, Thomson": "Central",
        "Balestier, Toa Payoh, Serangoon": "Central",
        "Bishan, Ang Mo Kio": "Central",
        "Macpherson, Braddell": "East",
        "Geylang, Eunos": "East",
        "Katong, Joo Chiat, Amber Road": "East",
        "Bedok, Upper East Coast, Eastwood, Kew Drive": "East",
        "Loyang, Changi": "East",
        "Tampines, Pasir Ris": "East",
        "Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang": "North",
        "Kranji, Woodgrove": "North",
        "Upper Thomson, Springleaf": "North",
        "Yishun, Sembawang": "North",
        "Serangoon Garden, Hougang, Ponggol": "North East",
        "Seletar": "North East",
        "Pasir Panjang, Hong Leong Garden, Clementi New Town": "West",
        "Upper Bukit Timah, Clementi Park, Ulu Pandan": "West",
        "Jurong": "West",
        "Lim Chu Kang, Tengah": "West"
        }

    urls = {}
    for district, district_code in districts.items():
        url = f'https://www.edgeprop.sg/property-search?listing_type=sale&property_type=13%2C75%2C76%2C77%2C78%2C79%2C80%2C81%2C82%2C83%2C84%2C85%2C86%2C87%2C88%2C89%2C90%2C91%2C92%2C93%2C94%2C95%2C96%2C97%2C98%2C99%2C100%2C101%2C102%2C134%2C135%2C136&district={district_code}&page={{page}}'
        urls[district] = url
    
   
    property_details = {
        "title": [], "price": [], "hdb_type": [], "area": [], "year": [], "price_per_sqft": [],
        "size_sqft": [], "road_name": [], "n_bedrooms": [], "n_bathrooms": [], "district": [], "region": []
    }

    for district, url in urls.items():
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'listing-card-name')]/h2")
            ))
        except:
            continue

        titles = driver.find_elements(By.XPATH, '//div[@class="jsx-911604640 listing-card-name"]/h2')
        prices = driver.find_elements(By.XPATH, '//div[@class="jsx-911604640 listing-card-price"]/a')
        descs = driver.find_elements(By.XPATH, '//div[contains(@class, "jsx-4147696354 desc-box")]')
        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'listing-card-detail')]")

        desc_texts = [el.text for el in descs]
        start_indices = [i for i, text in enumerate(desc_texts) if "HDB" in text]

        for i in range(min(len(titles), len(start_indices))):
            chunk = desc_texts[start_indices[i]:start_indices[i+1] if i+1 < len(start_indices) else len(desc_texts)]
            if len(chunk) < 5:
                continue

            try:
                text = cards[i].find_element(By.XPATH, './/span[@class="jsx-609329512"]/span').get_attribute('textContent')
                bed, bath = [s.strip() for s in text.split("|")]
            except:
                continue

            property_details['title'].append(titles[i].text)
            property_details['price'].append(prices[i].text)
            property_details['hdb_type'].append(chunk[0])
            property_details['area'].append(chunk[1])
            property_details['year'].append(chunk[2])
            property_details['price_per_sqft'].append(chunk[3] if len(chunk) > 3 else "")
            property_details['size_sqft'].append(chunk[4] if len(chunk) > 4 else "")
            property_details['road_name'].append(chunk[5] if len(chunk) > 5 else "")
            property_details['n_bedrooms'].append(bed)
            property_details['n_bathrooms'].append(bath)
            property_details['district'].append(district)
            property_details['region'].append(district_region[district])

        time.sleep(1)

    driver.quit()
    df = pd.DataFrame(property_details)
    df["scraped_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    #save
    SCRAPED_PATH = 'data/raw_data1.csv'
    df.to_csv(SCRAPED_PATH, index=False)
    print(f"✅ Scraped {len(df)} rows and saved to {SCRAPED_PATH}")
        
    return df
