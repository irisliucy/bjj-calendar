from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager

from utils import convert_date_string_to_obj, save_events_to_json

_EVENT_HOST_NAME = "ADCC"
_TODAY_STRING = datetime.now().strftime("%Y%m%d")

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)

def extract_event_per_page(event_selectors, events, event_cnt):
    for i, event_selector in enumerate(event_selectors):
        # i. Extract event date
        event_date_month = event_selector.find('span', class_='rw-date-month').get_text()
        event_date_day = event_selector.find('span', class_='rw-date-day').get_text()
        event_date_year = event_selector.find('span', class_='rw-date-year').get_text()
        event_start_date = convert_date_string_to_obj(event_date_month + ' ' + event_date_day + ' ' + event_date_year)
        event_end_date = event_start_date
        # ii. Extract event name
        event_name = event_selector.find('h2', class_='entry-title').get_text()
        # iii. Extract event location
        event_location = event_selector.find('p', class_='rw-event-location').get_text()
        # iv. Extract evemt link
        event_link = event_selector.find('a', attrs={'href': re.compile("^https://")}).get('href')
        events.append({"event_id": event_cnt,
                    "event_host": _EVENT_HOST_NAME,
                    "event_name": event_name, 
                    "event_start_date": event_start_date,
                    "event_end_date": event_end_date,
                    "event_venue":event_location,
                    "event_link": event_link
                    })
        event_cnt += 1
    return events, event_cnt

def refresh_page_source(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    return soup

# 1. Access ADCC championship page and click to display all events using selenium
driver.get("https://adcombat.com/adcc-events/")

# 2. Extract events using Beautiful Soup 
page_buttons = driver.find_elements(By.CLASS_NAME, "page")
next_page_button = driver.find_element(By.CLASS_NAME, "nextpostslink")
events = []
event_cnt = 0
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
event_selectors = soup.find_all('article', class_='row-eq-height')
events, event_cnt = extract_event_per_page(event_selectors, events, event_cnt) # extract event details in the original page
# Click "Next Page" & refresh the page source until there is no more page buttons
for x in range(len(page_buttons)):
    if page_buttons[x].is_displayed():
        driver.execute_script("arguments[0].click();", page_buttons[x])
        time.sleep(1)
        soup = refresh_page_source(driver)  # refresh page source
        event_selectors = soup.find_all('article', class_='row-eq-height')
        events, event_cnt = extract_event_per_page(event_selectors, events, event_cnt) # extract event details in the next page

# 3. Output event dictionary to JSON file
save_events_to_json(events, 'results/result_events_{}_{}.json'.format(_EVENT_HOST_NAME, _TODAY_STRING))