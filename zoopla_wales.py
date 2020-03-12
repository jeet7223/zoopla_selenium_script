import bs4
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
import time
import datetime
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup
from sqlescapy import sqlescape
import mysql.connector
from selenium.common.exceptions import NoSuchElementException
import sys

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="zoopla"
)

mycursor = mydb.cursor()

codes = []
path = "C:\\Users\\Business\\Downloads\\geckodriver-v0.26.0-win64\\geckodriver.exe"
driver = Firefox(executable_path=path)
browser = driver

area = str(sys.argv[1])
keyword = str(sys.argv[2])
home = 'https://www.zoopla.co.uk/for-sale/property/{}/?keywords={}&identifier={}&q={}&is_shared_ownership=false&is_retirement_home=false&search_source=home&page_size=100&radius=0'.format(area,keyword,area,area)
driver.get(home)
try:
    length2=len(browser.find_element_by_class_name('paginate').find_elements_by_tag_name('a'))
    total_pages = browser.find_element_by_class_name('paginate').find_elements_by_tag_name('a')[length2-2].get_attribute('innerHTML')
    value = int(total_pages)+1
except NoSuchElementException:
    total_pages= 0
    value = int(total_pages)+2
print(total_pages)
for page in range(1,value):
    print("pages no.",page)
    price = 'https://www.zoopla.co.uk/for-sale/property/{}/?keywords={}&identifier={}&q={}&is_shared_ownership=false&is_retirement_home=false&search_source=home&page_size=100&radius=0&pn={}'.format(area,keyword,area,area,page)
    driver.get(price)

    no_of_houses = browser.find_element_by_class_name('listing-results').find_elements_by_tag_name("li")

    for item in no_of_houses:
        li_id = item.get_attribute('data-listing-id')
        print(li_id)
        if li_id!=None:
            codes.append(li_id)
print('========================================')
print(codes)
print('========================================')
for zips in codes:
    try:
        driver.get('https://www.zoopla.co.uk/for-sale/details/{}'.format(zips))
        detail_urls = 'https://www.zoopla.co.uk/for-sale/details/{}?featured=1&utm_content=featured_listing'.format(zips)
        address = browser.find_element_by_class_name('ui-property-summary__address').get_attribute('innerHTML')
        postal_code = browser.find_element_by_class_name('ui-property-summary__address').get_attribute('innerHTML').split(' ')
        length = len(postal_code)
        postal_code_new = postal_code[length-1]
        bedroom_exist = len(browser.find_element_by_class_name('dp-features-list--counts').find_elements_by_tag_name('li'))
        bedroom = '0'
        if bedroom_exist >= 1:
            bedroom = browser.find_element_by_class_name('dp-features-list--counts').find_elements_by_tag_name('li')[0].find_element_by_tag_name('span').get_attribute('innerHTML').replace('bedrooms','').replace('bedroom','')
        bathroom = '0'
        bathroom_exist = len(browser.find_element_by_class_name('dp-features-list--counts').find_elements_by_tag_name('li'))
        if bathroom_exist >= 2:
            bathroom = browser.find_element_by_class_name('dp-features-list--counts').find_elements_by_tag_name('li')[1].find_element_by_tag_name('span').get_attribute('innerHTML').replace('bathrooms','').replace('bathroom','').replace('reception','').replace('rooms','').replace('room','')
        reception = '0'
        reception_exist = len(browser.find_element_by_class_name('dp-features-list--counts').find_elements_by_tag_name('li'))
        if reception_exist >= 3:
            reception = browser.find_element_by_class_name('dp-features-list--counts').find_elements_by_tag_name('li')[2].find_element_by_tag_name('span').get_attribute('innerHTML').replace('reception','').replace('room','').replace('rooms','').replace('s','')
        property_price = browser.find_element_by_class_name('ui-pricing__main-price').get_attribute('innerHTML').replace('\xA3','').replace(',','')
        property_type = browser.find_element_by_class_name('ui-property-summary__title').get_attribute('innerHTML')
        first_listed_date = browser.find_element_by_class_name('dp-price-history__item-date').get_attribute('innerHTML')
        first_listed_date_new = browser.find_element_by_class_name('dp-price-history__item-date').get_attribute('innerHTML').replace('th','').replace('rd','').replace('nd','').replace('st','')
        agent_name = browser.find_element_by_class_name('ui-agent__name').get_attribute('innerHTML')
        last_sold_exist = len(browser.find_element_by_class_name('dp-price-history-block').find_elements_by_tag_name('div'))
        last_sold = '0'
        if last_sold_exist==2:
            last_sold =browser.find_element_by_class_name('dp-price-history-block').find_elements_by_tag_name('div')[1].find_elements_by_tag_name('span')[1].get_attribute('innerHTML').replace('\xA3','').replace(',','')
            Price_Changes = int(property_price) - int(last_sold)
        else:
            Price_Changes = '0'
        date1 = datetime.datetime.strptime('{}'.format(first_listed_date_new), '%d %b %Y').strftime('%d,%m,%Y')
        today = date.today()
        today_new = datetime.datetime.strptime('{}'.format(today),'%Y-%m-%d').strftime('%d,%m,%Y')
        def days_between(d1, d2):

            d1 = datetime.datetime.strptime(d1,'%d,%m,%Y')
            d2 = datetime.datetime.strptime(d2,'%d,%m,%Y')
            return abs((d2 - d1).days)

        Changes_date = days_between('{}'.format(today_new),'{}'.format(date1))
        sql = """INSERT INTO zoopla_wales (Area,Keyword,Postal_code,Address,Bedrooms,Bathrooms,Receptions,Proerty_type,Property_price,Price_changes,Detail_urls,First_listed_date,Last_listed,Time_since_first_listed,Agent_name) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s','%s','%s',%s,'%s')""" % (sqlescape(area),sqlescape(keyword),postal_code_new,sqlescape(address),sqlescape(bedroom),sqlescape(bathroom),sqlescape(reception),sqlescape(property_type),sqlescape(property_price),Price_Changes,sqlescape(detail_urls),sqlescape(first_listed_date),sqlescape(last_sold),Changes_date,sqlescape(agent_name))
        mycursor.execute(sql)
        mydb.commit()

    except NoSuchElementException:
        address = 'N/A'
        bedroom = 'N/A'
        bathroom = 'N/A'
        reception = 'N/A'
        last_sold = 'N/A'
        Price_Changes = 'N/A'
        property_type = 'N/A'
        property_price = 'N/A'
        agent_name = 'N/A'
        first_listed_date = 'N/A'
        Changes_date = 'N/A'
        detail_urls = "N/A"
        postal_code = 'N/A'
    print('Detail URL-:'+detail_urls)
    print("Id number",zips)
    print('Address-:'+address)
    print('Bedrooms-:'+bedroom)
    print('Bathrooms-:'+bathroom)
    print('Reception Room=:'+reception)
    print('Property Type-:'+property_type)
    print('Property Price-:'+property_price)
    print('Last Sold-:'+last_sold)
    print('Price Changes-:',Price_Changes)
    print('First Listed Date-:'+first_listed_date)
    print('Time since first listed-:',Changes_date,'Days')
    print('Postal Code-:'+postal_code_new)
    print('Agent Name-:'+agent_name)
    print('=========================================================================================')
    # time.sleep(2)
browser.quit()
