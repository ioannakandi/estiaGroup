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
import pandas as pd
from flask import Flask, render_template, flash, request, Markup, session, Response, send_file
from flask_cors import CORS, cross_origin
import json

# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose shipping database
db = client['estiaGroup']
houses = db['houses']

# App config.
app = Flask(__name__, static_url_path='',
            static_folder='templates\classimax-premium',
            template_folder='templates\classimax-premium')
DEBUG = True
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
CORS(app)

#method to store the data retrieved from xe.gr in MongoDB
def storeData(location):
    if(location=="Trikala"):
        pages=2
    elif(location=="Mesologgi"):
        pages=3
    elif(location=="Crete"):
        pages=52
    
    print(location)
    for i in range (1,pages):
        html = open("data/"+location+"/"+location+"_"+str(pages)+".html",encoding="utf-8").read()
        soup = BeautifulSoup(html,features="lxml")
        try:
            for i in range(0,1000):
                soup_1 = soup.find_all('div', attrs = {'class':'results-content grid-x'})[0].find('div', attrs = {'class':'cell large-6 tiny-12 results-grid-container'}).find('div', attrs = {'class':'property-results-content'}).find_all('div', attrs = {'class':'property-result-list'})[1].find('div', attrs = {'class':'grid-x'}).find_all('div', attrs = {'class':'cell huge-3 xxxlarge-4 large-6 medium-4 small-6 tiny-12'})[i].find('div', attrs = {'class':'common-property-ad'}).find('div', attrs = {'class':'common-property-ad-body grid-y align-justify'}).find('a')
                title = soup_1.find('div', attrs = {'class':'common-property-ad-title'}).find('h3').text
                print(title)
                price = soup_1.find('div', attrs = {'class':'common-property-ad-price'}).find('span', attrs = {'class':'property-ad-price'}).text
                print(price)
                pricepersqm = soup_1.find('div', attrs = {'class':'common-property-ad-price'}).find('span', attrs = {'class':'property-ad-price-per-sqm'}).text
                print(pricepersqm)
                try:
                    level = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'property-ad-level-container'}).find('span', attrs = {'class':'property-ad-level'}).text
                except:
                    level = '0'
                print(level)
                if(location=='Trikala'):
                    try:
                        bedroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bedrooms-container'}).find('span').text
                    except:
                        bedroom = '1'
                    
                    try:
                        bathroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bathrooms-container'}).find('span').text
                    except:
                        bathroom = '1'
                    
                    try:
                        year = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-construction-year-container'}).find('span').text
                    except:
                        year = '1990'

                elif(location=='Crete'):
                    
                    try:
                        bedroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bedrooms-container'}).find('span').text
                    except:
                        bedroom = '1'
                    
                    try:
                        bathroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bathrooms-container'}).find('span').text
                    except:
                        bathroom = '1'
                    
                    try:
                        year = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-construction-year-container'}).find('span').text
                    except:
                        year = '1990'
                      
                elif(location=='Mesologgi'):
                    
                    try:
                        bedroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bedrooms-container'}).find('span').text
                    except:
                        bedroom = '1'
                    
                    try:
                        bathroom = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-bathrooms-container'}).find('span').text
                    except:
                        bathroom = '1'
                    
                    try:
                        year = soup_1.find('div', attrs = {'class':'common-property-ad-details grid-x'}).find('div', attrs = {'class':'grid-x property-ad-construction-year-container'}).find('span').text
                    except:
                        year = '1990'
                       
                estate = {}
                estate['title'] = title.strip()
                estate['price'] = int(price.strip().replace("€","").replace(".","").strip())
                print(estate['price'])
                estate['pricepersqm'] = int(pricepersqm.strip().replace("€/τ.μ.","").replace(".","").strip())
                print(estate['pricepersqm'])
                estate['level'] = int(level.strip().replace("ος","").replace("Ισόγειο","0").replace("Ημιυπόγειο","-1").replace(",","").strip())
                print(estate['level'])
                estate['bedroom'] = int(bedroom.strip().replace("×","").strip())
                print(estate['bedroom'])
                estate['bathroom'] = int(bathroom.strip().replace("×","").strip())
                print(estate['bathroom'])
                estate['year'] = int(year.strip().replace("×","").strip())
                print(estate['year'])
                estate['location'] = location
                print(estate['location'])
                print(estate)
                houses.insert_one(estate)
        except:
            pass


#method to retrieve the data from xe.gr         
def retrieveData(location):
    if(location=="Trikala"):  
        place = 'ChIJXy53IjMZWRMRwJ-54iy9AAQ' #Trikala
        for i in range (1,3):
            URL = "https://www.xe.gr/property/results?transaction_name=buy&item_type=re_residence&geo_place_ids%5B%5D=ChIJXy53IjMZWRMRwJ-54iy9AAQ&page="+str(i)
            r = requests.get(URL)
            soup = BeautifulSoup(r.content, 'html5lib')
            print(soup.prettify())
            with open("data/trikala/trikala_"+str(i)+".html", "w",encoding="utf-8") as file:
                file.write(str(soup.prettify()))
    elif(location=="Mesologgi"):
        place = 'ChIJoeIsf5luXhMRcIK54iy9AAQ' #Mesologgi
        for i in range (1,4):
            URL = "https://www.xe.gr/property/results?transaction_name=buy&item_type=re_residence&geo_place_ids%5B%5D=ChIJoeIsf5luXhMRcIK54iy9AAQ&page="+str(i)
            r = requests.get(URL)
            soup = BeautifulSoup(r.content, 'html5lib')
            print(soup.prettify())
            with open("data/mesologgi/mesologgi_"+str(i)+".html", "w",encoding="utf-8") as file:
                file.write(str(soup.prettify()))
    elif(location=="Crete"):
        place = '%5B%5D=ChIJoZh9gi_-mhQRMMa54iy9AAE' #Crete
        for i in range (1,53):
            URL = 'https://www.xe.gr/property/results?transaction_name=buy&item_type=re_residence&geo_place_ids%5B%5D=ChIJoZh9gi_-mhQRMMa54iy9AAE&page='+str(i)
            r = requests.get(URL)
            soup = BeautifulSoup(r.content, 'html5lib')
            print(soup.prettify())
            with open("crete_"+str(i)+".html", "w",encoding="utf-8") as file:
                file.write(str(soup.prettify()))


def getStatistics(location,level):
    if(level==0):
        query_cursor=houses.find({"location":location,"level":0},{"_id":0})
    else:
        query_cursor=houses.find({"location":location,"level":{"$ne" : 0}},{"_id":0})
    list_cur=list(query_cursor)
    df=pd.DataFrame(list_cur)
    print(df)
    statistics={}
    statistics["avg_price"]=int(df.pricepersqm.mean())
    statistics["avg_baths"]=int(df.bathroom.mean())
    statistics["avg_rooms"]=int(df.bedroom.mean())
    statistics["newest_house"]=int(df.year.max())
    statistics["oldest_house"]=int(df.year.min())
    return statistics

    
def getSelectedHouses(location,level):
    if(level=="ALL"):
        query_cursor=houses.find({"location":location},{"_id":0})
        list_cur=list(query_cursor)
        return list_cur
    elif(level=="Apartment"):
        query_cursor=houses.find({"location":location,"level":{"$ne" : 0}},{"_id":0})
        list_cur=list(query_cursor)
        return list_cur
    else:
        query_cursor=houses.find({"location":location,"level":0},{"_id":0})
        list_cur=list(query_cursor)
        return list_cur
   
#those are just for testing
#retrieveData("Mesologgi")
#storeData("Crete")
#getStatistics("Mesologgi",0)
#print(getSelectedHouses("Mesologgi",1))


#Flask endpoints
#Main endpoint that shows the main page of the app
@app.route("/")
@cross_origin()
def home():
    return render_template("index.html")

# endpoint for retrieving selected houses based on location and level
@app.route("/getSelectedHouses",methods=['GET', 'POST'])
@cross_origin()
def getSelectedHousesAPI():
    if request.method == 'GET':
        #get the needed arguments (location and level)
        location = request.args.get('location')
        level = request.args.get('level')
        #retrieve the data
        results = getSelectedHouses(location,level)
        return Response(json.dumps(results), status=200, mimetype="application/json")
    return Response('{"message":"Please try again"}', status=500, mimetype="application/json")

# endpoint for retrieving statistics for houses in selected area
@app.route("/getStatistics",methods=['GET', 'POST'])
@cross_origin()
def getStatisticsAPI():
    if request.method == 'GET':
        #get the needed arguments (location and level)
        location = request.args.get('location')
        level = request.args.get('level')
        #retrieve the data
        results = getStatistics(location,int(level))
        return Response(json.dumps(results), status=200, mimetype="application/json")
    return Response('{"message":"Please try again"}', status=500, mimetype="application/json")


if __name__ == "__main__":
   app.run(debug=True, host='0.0.0.0', port=5000)