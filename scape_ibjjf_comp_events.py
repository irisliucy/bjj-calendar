from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager

def parse_events_date(raw_date_string):
    raw_date_string = [x.strip() for x in event_date.split(' - ')]
    if len(raw_date_string) > 1:
        event_start_date, event_end_date = raw_date_string
    else:
        event_start_date = raw_date_string[0]
        event_end_date = event_start_date
    return event_start_date, event_end_date

def save_events_to_json(all_event_info, saved_to):
    """ Save IBJJF event details to json."""
    with open(saved_to, 'w') as jout:   
        json.dump(all_event_info, jout)
    print("Yay! Scraped events are saved to {}!".format(saved_to))

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)

# 1. Access IBJJF championship page and click to display all events using selenium
driver.get("https://ibjjf.com/events/calendar")
# IBJJF Hack: click "view all" to display all championships & wait
show_all_buttons = driver.find_element(By.CLASS_NAME, "search-results-action").click()
time.sleep(1)

# 2. Extract events using Beautiful Soup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
events = []
event_selectors = soup.find_all('div', class_='event-row')
for i, event_selector in enumerate(event_selectors):
    event_date = event_selector.find('div', class_='date').get_text()
    event_start_date, event_end_date = parse_events_date(event_date)
    event_name = event_selector.find('div', class_='name').get_text()
    event_location = event_selector.find('div', class_='local').get_text()
    events.append({"event_id": i,
                   "event_host": "IBJJF",
                   "event_name": event_name, 
                   "event_start_date": event_start_date,
                   "event_end_date": event_end_date,
                   "event_venue":event_location})

# 3. Output event dictionary to JSON file
# print("Adding: ", events)
save_events_to_json(events, 'ibjjf_events.json')
    
    

