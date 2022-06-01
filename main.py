# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 10:32:59 2022

@author: Ioanna Kandi & Kostis Mavrogiorgos
"""

import requests
from bs4 import BeautifulSoup
import csv
import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import time, os, sys

# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose shipping database
db = client['estiaGroup']
houses = db['houses']


def storeData(location):
    if(location=="Trikala"):
        html = open("output1.html",encoding="utf-8").read()
        location = "Τρίκαλα"
    elif(location=="Mesologgi"):
        html = open("mesologgi.html",encoding="utf-8").read()
        location = "Μεσολόγγι"
    
    soup = BeautifulSoup(html,features="lxml")
    #list to store properties
    properties=[]  # a list to store quotes
    try:
        for i in range(0,1000):
            soup_1 = soup.find_all('div', attrs = {'class':'results-content grid-x'})[0].find('div', attrs = {'class':'cell large-6 tiny-12 results-grid-container'}).find('div', attrs = {'class':'property-results-content'}).find_all('div', attrs = {'class':'property-result-list'})[1].find('div', attrs = {'class':'grid-x'}).find_all('div', attrs = {'class':'cell huge-3 xxxlarge-4 large-6 medium-4 small-6 tiny-12'})[i].find('div', attrs = {'class':'common-property-ad'}).find('div', attrs = {'class':'common-property-ad-body grid-y align-justify'}).find('a')
            title = soup_1.find('div', attrs = {'class':'common-property-ad-title'}).find('h3').text
            print(title)
            price = soup_1.find('div', attrs = {'class':'common-property-ad-price'}).find('span', attrs = {'class':'property-ad-price'}).text
            print(price)
            pricepersqm = soup_1.find('div', attrs = {'class':'common-property-ad-price'}).find('span', attrs = {'class':'property-ad-price-per-sqm'}).text
            print(pricepersqm)
            level = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'property-ad-level-container'}).find('span', attrs = {'class':'property-ad-level'}).text
            print(level)
            bedroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bedrooms-container'}).find('span').text
            print(bedroom)
            bathroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bathrooms-container'}).find('span').text
            print(bathroom)
            year = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-construction-year-container'}).find('span').text
            print(year)
            estate = {}
            estate['title'] = title.strip()
            estate['price'] = price.strip()
            estate['pricepersqm'] = pricepersqm.strip()
            estate['level'] = level.strip()
            estate['bedroom'] = bedroom.strip()
            estate['bathroom'] = bathroom.strip()
            estate['year'] = year.strip()
            estate['location'] = location
            print(estate)
            properties.append(estate)
            x = houses.insert_one(estate)
    except:
        pass


         
def retrieveData(location):
    if(location=="Trikala"):  
        place = 'ChIJXy53IjMZWRMRwJ-54iy9AAQ' #Trikala
        URL = "https://www.xe.gr/property/results?transaction_name=buy&item_type=re_residence&geo_place_ids[]="+location
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html5lib')
        print(soup.prettify())
        with open("trikala.html", "w",encoding="utf-8") as file:
            file.write(str(soup.prettify()))
    elif(location=="Mesologgi"):
        place = 'ChIJoeIsf5luXhMRcIK54iy9AAQ' #Mesologgi
        URL = "https://www.xe.gr/property/results?transaction_name=buy&item_type=re_residence&geo_place_ids[]="+location
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html5lib')
        print(soup.prettify())
        with open("mesologgi.html", "w",encoding="utf-8") as file:
            file.write(str(soup.prettify()))

#retrieveData("Mesologgi")
#storeData("Mesologgi")

'''
#list to store properties
properties=[]  # a list to store quotes
for counter in range(1,3):
    URL = "https://www.xe.gr/property/results?transaction_name=buy&item_type=re_residence&geo_place_ids[]="+place+"&page="+str(counter)
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    print(soup.prettify())
    with open("output1.html", "w",encoding="utf-8") as file:
        file.write(str(soup.prettify()))
    table = soup.find('div', attrs = {'class':'results-content grid-x'}).find('div', attrs = {'class':'property-result-list'})
    print(table)
    for row in table.findAll('div',
                         attrs = {'class':'common-property-ad-price'}):
        estate = {}
        estate['price'] = row.h3.text
        
        estate['url'] = row.a['href']
        estate['img'] = row.img['src']
        estate['lines'] = row.img['alt'].split(" #")[0]
        estate['author'] = row.img['alt'].split(" #")[1]
        
        properties.append(estate)
      
    filename = 'properties.csv'
    with open(filename, 'w', newline='') as f:
        w = csv.DictWriter(f,['theme','url','img','lines','author'])
        w.writeheader()
        for house in properties:
            w.writerow(house)
'''   