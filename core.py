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

#ASIN SAVE COUNTER
SAVE_COUNTER=100
OUTPUT_FOLDER="Z:\\ProjectAmazon\\Scrapping_Output"

class ExtractAmazonData:
    def __init__(self,baseFile):
        self.base_file=pd.read_csv(baseFile)
        self.total_count=len(self.base_file)
        if self.total_count==0:
            print("Not a Valid File")
        else:
            print("Data Loaded")

        self.OpenAmazon()

    #Method to Locate the Title
    def GetListingTitle(self,source_data):
        soup=self.source_Data
        title=soup.find("span",id="productTitle").text
        title=title.replace('\n','')
        title=title.strip()
        return title

    #Method to Locate the Brand
    def GetListingBrand(self,source_data):
        soup=self.source_Data
        brand_unfiltered=soup.find('div',{"id":"bylineInfo_feature_div"})
 #       brand_filtered=brand_unfiltered.find_next("a",href=True)
        brand_unfiltered=str(brand_unfiltered.get_text())
        brand_filtered=brand_unfiltered.strip()
        return brand_filtered

    #Method to Locate the Brand
    def GetSupplier(self,source_data):
        soup=self.source_Data
        supplier_name=""
        d=soup.find_all('span',{"id":"tabular-buybox-truncate-1"})
        for k in d:
            if d is not None:
                for supplier in d:
                    for s in supplier:
                        supplier_name=s.text
                        break

        if len(supplier_name)==0:
            return "Null"

        return supplier_name



    #Method to Extract the Pricing of the Product - Current Price, Original Price, Savings
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

        #Get Product Ratings

    #Method to Extract Product Rating
    def GetProductRating(self,source_data):
        soup=self.source_Data
        try:
            unfiltered=soup.find("div",{"class":"a-fixed-left-grid AverageCustomerReviews a-spacing-small"})
            for t in unfiltered:
                o=t.text
        except:
            try:
                unfiltered=soup.find("span",{"class":"reviewCountTextLinkedHistogram noUnderline","span":"a-icon-alt"})
                level_1_filter=unfiltered.find("span",{"class":"a-icon-alt"})
                o=level_1_filter.text
            except:
                o="No Stars Found"
        return o.strip()

    #Method to Extract Product Rating
    def GetProductDescription(self,source_data):
        soup=self.source_Data
        try:
            unfiltered=soup.find("div",{"id":"featurebullets_feature_div"}).text
        except:
            pass
        return unfiltered.strip()

    #Method to Extract Quantities
    def GetProductQuantities(self,source_Data):
        soup=self.source_Data
        try:
            quantities=(len(soup.find("select",{"name":"quantity"}))-1)/2
        except:
            quantities=0

        return quantities

    #Method to Get technical Information for the Product
    def GetTechDetails(self,source_Data):
        soup=source_Data
        technical_header_list=""
        technical_data_list=""
        p=soup.find_all("table",{"id":"productDetails_techSpec_section_1"})

        for rows in p:
            header=rows.find_all('th')
            header_data=rows.find_all('td')
            try:
                for th in header:
                    technical_header_list=th.text+'||'+technical_header_list
 #                   header_list.append(th.text)

                for td in header_data:
                    technical_data_list=td.text+'||'+technical_data_list
#                    data_list.append(td.text)
            except:
                pass
            combList=technical_header_list+'----'+technical_data_list
            return str(combList).strip()

    # Getting the Technical Details
    def GetAdditionalDetails(self,source_Data):
            soup=source_Data
            additional_header_list=""
            additional_data_list=""
            p=soup.find_all("table",{"id":"productDetails_techSpec_section_1"})
            p=soup.find_all("table",{"id":"productDetails_detailBullets_sections1"})
            for rows in p:
                header=rows.find_all('th')
                header_data=rows.find_all('td')
                for th in header:
                    additional_header_list=th.text+'||'+additional_header_list
#                    header_list.append(th.text)
                for td in header_data:
                    additional_data_list=td.text+'||'+additional_data_list
 #                   data_list.append(td.text)

            combList=additional_header_list+'----'+additional_data_list
            return str(combList).strip()

    #Method to get Product Image Sources
    def GetImageSources(self,source_Data):
        soup=self.source_Data
        data=str(soup.find_all('script',type='text/javascript'))
        pattern = re.compile(r'"hiRes":"https://images-na.ssl-images-amazon.com/images/I/')
        b=re.finditer(pattern,data)
        sleep(2)
        o=""
        for dd in b:
            o=data[dd.start()+9:dd.end()+27]+"|"+o
        return o.strip()

    def OpenAmazon(self):
        exportdf=pd.DataFrame(columns=['SKU','Localized For','Brand/Title','Product_Desc','Pic_URL','Condition','Quantity'
                                       ,'Channel ID','Category','Shipping Policy','Payment Policy',
                                       'Return Policy','List Price','Stars','Brand','Technical','Additional','Supplier','Product_Description'])
        options = webdriver.ChromeOptions()
        options.add_experimental_option('useAutomationExtension', False)
        self.driver= webdriver.Chrome(options=options)
        self.driver.set_window_position(0,0)
        i=0
        for asin,row in self.base_file.iterrows():
            self.driver.get(row['Websites'])
            print(f"Extracting Data for {row['ASIN']}:(Remaining:{str(self.total_count-i)})")
            sleep(3)
            self.source_Data=BeautifulSoup(self.driver.page_source,features="lxml")
            sleep(2)
            try:
                self.base_title=self.GetListingTitle(self.source_Data)
            except:
                self.base_title="NULL"
            try:
                self.base_brand=self.GetListingBrand(self.source_Data)
            except:
                self.base_brand="NULL"
            try:
                self.base_price=self.GetProductPrice(self.source_Data)
            except:
                self.base_price="NULL"
            try:
                self.base_star_rating=self.GetProductRating(self.source_Data)
            except:
                self.base_star_rating="NULL"
            try:
                self.base_productQuantities=self.GetProductQuantities(self.source_Data)
            except:
                self.base_productQuantities="NULL"
            try:
                self.base_technical_Details=self.GetTechDetails(self.source_Data)
            except:
                self.base_technical_Details="NULL"
            try:
                self.base_additional_Details=self.GetAdditionalDetails(self.source_Data)
            except:
                self.base_additional_Details="NULL"
            try:
                self.base_image_sources=self.GetImageSources(self.source_Data)
            except:
                self.base_image_sources="NULL"

            try:
                self.base_supplier=self.GetSupplier(self.source_Data)
            except:
                self.base_supplier="NULL"        

            try:
                self.base_product_desc=self.GetProductDescription(self.source_Data)
            except:
                self.base_product_desc="NULL"   



            newData=[]
            newData=[row['ASIN'],'en_AU',self.base_brand,self.base_title,
                        self.base_image_sources,'NEW',self.base_productQuantities,'EBAY_AU',
                        row['EBAY_CAT'],'Flat:Australia Post(Free),Australia Post,1 bu'
                     ,'Payment','Returns Accepted,Buyer,30 Days',self.base_price,
                     self.base_star_rating,self.base_brand,
                     self.base_technical_Details,self.base_additional_Details,self.base_supplier,self.base_product_desc]
            i=i+1
            exportdf.loc[len(exportdf)]=newData


            if i%SAVE_COUNTER==0:
            	exportdf.to_csv(OUTPUT_FOLDER+"\\"+f'final_{i}.csv')

        print("Data Export Complete")
        self.driver.quit()



# ExtractAmazonData('ASIN.csv')