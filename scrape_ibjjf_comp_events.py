from bs4 import BeautifulSoup
import datetime
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager

from utils import convert_date_string_to_obj, save_events_to_json

_EVENT_HOST_NAME = "IBJJF"
_TODAY_STRING = datetime.datetime.now().strftime("%Y%m%d")
_IS_START_DATE_ESTIMATED = False
_IS_END_DATE_ESTIMATED = False

def is_date_estimated(date_string):
    # Check if there is specicial character "*" at the end of the date. If yes, mark True. 
    estimated_date_char = '*'
    if date_string[-1] == estimated_date_char:
        date_string = date_string.replace(estimated_date_char,"")
        return True, date_string
    return False, date_string

def parse_events_date(raw_date_string):
    global _IS_START_DATE_ESTIMATED, _IS_END_DATE_ESTIMATED
    """Parse IBJJF date string."""
    raw_date_string = [x.strip() for x in raw_date_string.split(' - ')]
    this_year = datetime.date.today().year
    # check if event date is estimated
    _IS_START_DATE_ESTIMATED, raw_start_date = is_date_estimated(raw_date_string[0])
    if len(raw_date_string) > 1:
        _IS_END_DATE_ESTIMATED, raw_end_date = is_date_estimated(raw_date_string[1])
        # event_start_date, event_end_date = raw_date_string
        event_start_date = raw_start_date + ' ' + str(this_year)
        event_end_date = raw_end_date + ' ' + str(this_year)
    else:
        _IS_END_DATE_ESTIMATED = _IS_START_DATE_ESTIMATED
        event_start_date = raw_start_date + ' ' + str(this_year)
        event_end_date = event_start_date
    return convert_date_string_to_obj(event_start_date) , convert_date_string_to_obj(event_end_date)

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
    # i. Extract event date
    event_date = event_selector.find('div', class_='date').get_text()
    event_start_date, event_end_date = parse_events_date(event_date)
    # ii. Extract event name
    event_name = event_selector.find('div', class_='name').get_text()
    # iii. Extract event location
    event_location = event_selector.find('div', class_='local').get_text()
    # present_event_link = event_selector.find('a', attrs={'href': re.compile("^https://")})
    # if present_event_link != None:
    #     event_link = present_event_link.get('href')
    event_link = ""
    events.append({"event_id": i,
                   "event_host": _EVENT_HOST_NAME,
                   "event_name": event_name, 
                   "event_start_date": event_start_date,
                   "event_end_date": event_end_date,
                   "is_event_start_date_estimated": _IS_START_DATE_ESTIMATED, 
                   "is_event_end_date_estimated": _IS_END_DATE_ESTIMATED,
                   "event_venue":event_location,
                   "event_link": event_link
                   })


# 3. Output event dictionary to JSON file
# print("Adding: ", events)
save_events_to_json(events, 'results/result_events_{}_{}.json'.format(_EVENT_HOST_NAME, _TODAY_STRING))
    
    

