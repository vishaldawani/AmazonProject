#Developer: Vishal Dawani
#Version 1.0
#This version will get the data from the Amazon and store it in a dataframe
# Purpose: Scrapes data from Amazon

#Import Libraries
import os
import pandas as pd
import sys
import re
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import math


#VAR
MARGIN=0.4
MAX_MIN_PRICE_RANGE=1
OUTPUT_FILE_NAME = 'update_Inventory_' #concatanate this name with the output number of the file e.g: update_inventory_ +  1.csv
INPUT_FILE_NAME = 'UploadAsins - Orginal.csv'

class Update_Ebay_Inventory:
    def __init__(self,baseFile, file_number,line_count = 750):
        self.start_point = (file_number - 1) * line_count   #(file_number - 1) * line_count = starting point of the csv 
        self.file_number = file_number
        self.base_file=pd.read_csv(baseFile)#,skiprows = self.start_point)
        self.total_count=len(self.base_file)
        self.line_count = line_count
        self.Errors = []
        #print (start_point)

        if self.total_count==0:
            print("Not a Valid File")
        else:
            print("Data Loaded")
        self.delete_file()
        sleep(2)
        self.OpenAmazon()

    def delete_file(self):
        if os.path.exists(os.getcwd()+'\\'+ OUTPUT_FILE_NAME):
            os.remove(os.getcwd()+'\\'+ OUTPUT_FILE_NAME)

    def GetProductPrice(self,source_data):
        soup=self.source_Data
        try:
            all_prices=soup.find("div",{"id":"unifiedPrice_feature_div"})
            current_price=all_prices.find("span",{"id":"priceblock_ourprice"})
            for price in current_price:
                retailRRP=price
        except:
            try:
                all_prices=soup.find("div",{"id":"unifiedPrice_feature_div"})
                current_price=all_prices.find("span",{"id":"priceblock_saleprice"})
                for price in current_price:
                    retailRRP=price
            except:
                print("Out of Stocks")
        return retailRRP.strip()
    
    def UpdatePrices(self,x):


        def compare_prices(x,y,max_min_logic):
            if max_min_logic==1:
                new_price=max(x,y)
            else:
                new_price=min(x,y)

            return new_price

        def addMargintoPrice(price):
            if price==0:
                return 0
            if isinstance(price,float):
                price_with_margin=price/(1-MARGIN)
                adjusted_price=math.ceil(price_with_margin)
                tweaked_price=adjusted_price-0.01
                return tweaked_price
        
    
        temp_price=str(x)
        if temp_price.find(" - ",1)>0:
            #Logic to Pick Max/Min Range
            PRICE_1=temp_price[:temp_price.find("-",1)]
            PRICE_2=temp_price[temp_price.find(" -",1)+2:]
            PRICE_1_A=PRICE_1.replace("$","")
            PRICE_1_A=PRICE_1_A.replace(",","")
            PRICE_1_A=float(PRICE_1_A)
            PRICE_2_A=PRICE_2.replace("$","")
            PRICE_2_A=PRICE_2_A.replace(",","")
            PRICE_2_A=float(PRICE_2_A)
            prices=(compare_prices(PRICE_1_A, PRICE_2_A,MAX_MIN_PRICE_RANGE))

        elif temp_price=='nan':
            prices=0
        else:
            prices=temp_price.replace(",","")
            prices=prices.replace("$","")
            prices=float(prices)
    
        prices_new=addMargintoPrice(prices)
        return prices_new

    #Method to Extract Quantities
    def GetProductQuantities(self,source_Data):
        soup=self.source_Data
        try:
            quantities=(len(soup.find("select",{"name":"quantity"}))-1)/2
        except:
            quantities=0

        return quantities

    #Method to Locate the Brand
    def GetShipsFrom(self,source_data):
        soup=self.source_Data
        shipment=""
        d=soup.find_all('span',{"id":"tabular-buybox-truncate-0"})
        for k in d:
            if d is not None:
                for shipment in d:
                    for s in shipment:
                        shipment_name=s.text
                        break

        if len(shipment_name)==0:
            return "Null"

        if shipment_name=='Amazon AU':
            return 1 #indicates FBA
        else:
            return 0 #indicates nonFBA

        return  0


    def OpenAmazon(self):
        exportdf=pd.DataFrame(columns=['SKU','Channel ID','Total Ship to Home Quantity','List Price'])
        options = webdriver.ChromeOptions()
        options.add_argument('--dns-prefetch-disable')
        options.add_experimental_option('useAutomationExtension', False)
        self.driver= webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(200)
        self.driver.set_window_position(0,0)
        i=0

        for asin,row in self.base_file.iloc[self.start_point:self.start_point+750].iterrows():  #The iloc will determine the start point of the csv
            #print(row['Websites']
            try:
                self.driver.get(row['Websites'])
            except TimeoutException as ex:
                self.Errors.append(row['ASIN'] +'-' + str(ex))
                continue
            print(f"Extracting Data for file_number: {self.file_number}, row_number : {self.file_number * self.line_count + i} ASIN: {row['ASIN']}:(Remaining:{str(self.line_count -i)})")
            sleep(2)
            self.source_Data=BeautifulSoup(self.driver.page_source,features="lxml")
            sleep(2)
            try:
                tempPrice=self.GetProductPrice(self.source_Data)
                final_price_adjusted=self.UpdatePrices(tempPrice)
                self.base_price=final_price_adjusted
            
            except:
                self.base_price="NULL"

            try:
                tempShipmentName=self.GetShipsFrom(self.source_Data)
                self.shipsFrom=tempShipmentName
            except:
                self.shipsFrom="NULL"

            try:
                temp_inventory=self.GetProductQuantities(self.source_Data)
                if temp_inventory>=5 and self.shipsFrom==1:
                    self.base_productQuantities=1
                else:
                    self.base_productQuantities=0

            except:
                self.base_productQuantities="NULL"

            # DATA SANITY CHECKS
            
            if self.base_price=="NULL":
                self.base_price = ""
                self.base_productQuantities=0
            else:
                pass

            if self.base_productQuantities=="NULL":
                self.base_productQuantities=0
            else:
                pass

  
            newData=[]
            newData=[row['ASIN'],'EBAY_AU',self.base_productQuantities,self.base_price]
            i=i+1
            exportdf.loc[len(exportdf)]=newData

        #print(self.base_price)
        
        exportdf.to_csv(OUTPUT_FILE_NAME + str(self.file_number) +".csv")
        print("Data Export Complete")
        #Export all the errors into a seperate file
        errordf = pd.DataFrame(np.array(self.errors).reshape(len(self.errors),1),columns = list('e'))
        
        errorsdf.to_csv(OUTPUT_FILE_NAME + str(self.file_number) +".csv")
        self.driver.close()
        self.driver.quit()


#Will run this function in the threading module, rather than here.
