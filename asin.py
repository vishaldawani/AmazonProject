# # Developer: Vishal Dawani
# # This code will try to scrape through the ASIN numbers and have them exported

# #Declare Variables

from bs4 import BeautifulSoup
from selenium import webdriver
import sys
from time import sleep
import pandas as pd
import numpy as np

def ScrapeAsins(website_link,ebay_category,total_pagescrape_count,category,Prime_Flag=True,star_count=4):

        asin_list=[]
        href_list=[]
        website_link=website_link
        category_code=ebay_category
        total_count=total_pagescrape_count
        Prime_Flag=Prime_Flag
        star_Count=star_count
        options = webdriver.ChromeOptions()
        options.add_experimental_option('useAutomationExtension', False)
        driver= webdriver.Chrome(options=options)
        driver.set_window_position(0,0)        
        for k in range(1,total_count+1):
            website=website_link
            website=website+str(k)
            driver.get(website)
            sleep(5)
            page_source=driver.page_source
            soup=BeautifulSoup(page_source,"lxml")
            try:
                for i in range(0,24*total_count):
                    data=soup.find_all("div",{"data-index":i})
                    asin_list.append(data[0]["data-asin"])
                    href_list.append("https://www.amazon.com.au/gp/product/"+str(data[0]["data-asin"]))
            except:
                    pass

            data=""
            websites_dynamic=""
            sleep(5)
        new_frame=pd.DataFrame({'ASIN':asin_list,'Websites':href_list,'Ebay':category_code,'Pages':total_count})
        filtered=new_frame["ASIN"]!=""
        dfNew=new_frame[filtered]
        k=0               # RESET INDEX
        
        return dfNew        



