from bs4 import BeautifulSoup
import datetime
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager

from utils import convert_date_string_to_obj, save_events_to_json

_EVENT_HOST_NAME = "JJWL"
_TODAY_STRING = datetime.datetime.now().strftime("%Y%m%d")

def extract_event_per_page(event_selectors, events, event_cnt):
    """Extract event from the full schedule page"""
    for i, event_selector in enumerate(event_selectors):
            group_events = event_selector.find_all('a', class_='single_tournament')
            this_year = datetime.date.today().year
            for e in group_events:
                # i. Extract event date
                event_date_month = event_selector.find('span', class_='month').get_text()
                event_date_day = event_selector.find('span', class_='day').get_text()
                event_start_date = convert_date_string_to_obj(event_date_month + ' ' + event_date_day + ' ' + str(this_year))
                event_end_date = event_start_date
                # ii. Extract event name
                event_name = e.find('h3', class_='eventname').get_text()
                # iii. Extract event location
                event_location = event_selector.find('small', class_='eventinfo').get_text()
                event_location = event_location.replace(" |", ",")
                # iv. Extract event link
                event_link = e.get('href')  # Hack: remove .. and replace with full link
                event_link = event_link.replace("..", "https://www.jjworldleague.com")
                events.append({"event_id": event_cnt,
                            "event_host": _EVENT_HOST_NAME,
                            "event_name": event_name, 
                            "event_start_date": event_start_date,
                            "event_end_date": event_end_date,
                            "event_venue": event_location,
                            "event_link": event_link,
                            })
                event_cnt += 1
    return events, event_cnt

def refresh_page_source(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    return soup

def refresh_page_and_scrape_events(driver, event_selectors, events, event_cnt):
    soup = refresh_page_source(driver)
    event_selectors = soup.find_all('div', class_='indicator')
    events, event_cnt = extract_event_per_page(event_selectors, events, event_cnt)
    return events, event_cnt

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)

# 1. Access JJWL championship page and click to display all events using selenium
driver.get("https://www.jjworldleague.com/")

# 2. Extract events using Beautiful Soup 
# JJWL Hack: There are two types of event types, Adult and Youth. Click "Full Schedule" for the details
events = []
event_cnt = 0
soup = refresh_page_source(driver)
event_selectors = soup.find_all('div', class_='indicator')
events, event_cnt = refresh_page_and_scrape_events(driver, event_selectors, events, event_cnt) # extract event details in the landing page
# Click "Youth Page" & refresh the page source 
youth_page = driver.find_element(By.CLASS_NAME, "young").click() 
time.sleep(1)
events, event_cnt = refresh_page_and_scrape_events(driver, event_selectors, events, event_cnt)# extract event details in the youth page


# 3. Output event dictionary to JSON file
# print("Adding: ", events)
save_events_to_json(events, 'results/result_events_{}_{}.json'.format(_EVENT_HOST_NAME, _TODAY_STRING))
    
    

