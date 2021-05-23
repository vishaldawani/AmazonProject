## Combine Core and ASIN

""""
doc:string

This run the entire model 

"""


# Model Settings

New_ASIN_Load   =0			# 0 means no new asins will be pulled
Amazon_Data     =0			# 0 means no new scrapping for the currently existing ASINS will happen
Data_Cleanse    =0			# 0 means data will not be cleansed
Ebay_Export     =0			# 0 ebay format will not happen
Ebay_Data_Cleanse=1		    # 1 MEANS EBAY DATA WILL BE CLEANSED


# Declare Variables For ASIN 
LINKS_FILE="Links - Sheet1.csv"
ASIN_LOCATION="Z:\ProjectAmazon"
ASIN_OUTPUT_FILE='ASIN.csv'
PRIME_ONLY=True					#INPUT FOR ASIN
STARS_COUNT=4 					#INPUT FOR ASIN
REQUIRE_NEW_ASIN=False

#STRUCTURING EBAY TEMPLATE INPUTS
EBAY_TEMPLATE_NAME='EbayTemplate.csv'
CLEANSED_DATA_FILE='cleansed.csv'
##TOP_PRODUCT_FILE='Top_products.csv'
TOP_PRODUCT_FILE=CLEANSED_DATA_FILE
EBAY_OUTPUT_FILE_NAME='ebay_export_step_1.csv'

#Custom Prepared Libraries
from asin import ScrapeAsins
from cleanse import FinalCleanups_v2
from core import ExtractAmazonData
from ebay_fixes import Attribute_Adjustments

#External Dependencies
import pandas as pd
import numpy as np
import os
from time import sleep
import tkinter

# Data ASIN 

def GetAllAsins(input_file):
	files=[file for file in os.listdir(ASIN_LOCATION) if file==ASIN_OUTPUT_FILE]
	if len(files)>0:
		os.remove(ASIN_LOCATION+"\\"+ASIN_OUTPUT_FILE)
		print("Previous ASIN File Deleted")	
	df=pd.read_csv(input_file)
	links_list=df['Amazon Link']
	counter=0
	for counter in range(0,len(links_list)):
		data=ScrapeAsins(links_list[counter], df['Ebay'].iloc[counter], df['Pages'].iloc[counter],df['Category'].iloc[counter])
		data.to_csv(ASIN_OUTPUT_FILE,mode='a',header=False)
		counter+=1

	result_df=pd.read_csv(ASIN_LOCATION+"\\"+ASIN_OUTPUT_FILE,header=None)
	result_df.rename(columns={0:"Index",1:"ASIN",2:"Websites",3:"EBAY_CAT",4:"Page_Count"},inplace=True)
	result_df.drop (columns=['Index'],inplace=True)
	result_df.to_csv(ASIN_OUTPUT_FILE)
	return result_df	

def PrepareforEbayExport():
	fields = ['SKU']
	base_data=pd.read_csv(ASIN_LOCATION+"\\"+CLEANSED_DATA_FILE)
	template_data=pd.read_csv(ASIN_LOCATION+"\\"+EBAY_TEMPLATE_NAME)			# Reqired_DF
	top_product=pd.read_csv(ASIN_LOCATION+"\\"+TOP_PRODUCT_FILE,usecols=fields,skipinitialspace=True)
	counter=0
	sku_list=[]	
	tempdf=pd.DataFrame(
						columns=[

								'SKU', 'Localized For', 'Variation Group ID', 'Variation Specific Name 1', 'Variation Specific Value 1',
								'Variation Specific Name 2', 'Variation Specific Value 2', 'Variation Specific Name 3', 'Variation Specific Value 3',
								'Variation Specific Name 4', 'Variation Specific Value 4', 'Variation Specific Name 5', 'Variation Specific Value 5',
								'Title', 'Subtitle', 'Product Description', 'Additional Info', 'Group Picture URL', 'Picture URL 1', 'Picture URL 2', 
								'Picture URL 3', 'Picture URL 4', 'Picture URL 5', 'Picture URL 6', 'Picture URL 7', 'Picture URL 8', 'Picture URL 9',
								'Picture URL 10', 'Picture URL 11', 'Picture URL 12', 'UPC', 'ISBN', 'EAN', 'MPN', 'Brand', 'ePID', 'Attribute Name 1',
								'Attribute Value 1', 'Attribute Name 2', 'Attribute Value 2', 'Attribute Name 3', 'Attribute Value 3', 'Attribute Name 4',
								'Attribute Value 4', 'Attribute Name 5', 'Attribute Value 5', 'Attribute Name 6', 'Attribute Value 6', 'Attribute Name 7',
								'Attribute Value 7', 'Attribute Name 8', 'Attribute Value 8', 'Attribute Name 9', 'Attribute Value 9', 'Attribute Name 10',
								'Attribute Value 10', 'Attribute Name 11', 'Attribute Value 11', 'Attribute Name 12', 'Attribute Value 12', 'Attribute Name 13',
								'Attribute Value 13', 'Attribute Name 14', 'Attribute Value 14', 'Attribute Name 15', 'Attribute Value 15', 'Attribute Name 16',
								'Attribute Value 16', 'Attribute Name 17', 'Attribute Value 17', 'Attribute Name 18', 'Attribute Value 18', 'Attribute Name 19',
								'Attribute Value 19', 'Attribute Name 20', 'Attribute Value 20', 'Attribute Name 21', 'Attribute Value 21', 'Attribute Name 22',
								'Attribute Value 22', 'Attribute Name 23', 'Attribute Value 23', 'Attribute Name 24', 'Attribute Value 24', 'Attribute Name 25',
								'Attribute Value 25', 'Condition', 'Condition Description', 'Measurement System', 'Length', 'Width', 'Height', 'Weight Major',
								'Weight Minor', 'Package Type', 'Total Ship To Home Quantity', 'Channel ID', 'Category', 'Shipping Policy', 'Payment Policy',
								'Return Policy', 'List Price', 'Max Quantity Per Buyer', 'Strikethrough Price', 'Minimum Advertised Price ', 'Minimum Advertised Price Handling',
								'Store Category Name 1', 'Store Category Name 2', 'Sold Off Ebay', 'Sold On Ebay', 'Apply Tax', 'Tax Category', 'VAT Percent',
								'Include eBay Product Details', 'Domestic Shipping P1 Cost', 'Domestic Shipping P1 Additional Cost', 
								'Domestic Shipping P1 Surcharge', 'Domestic Shipping P2 Cost', 'Domestic Shipping P2 Additional Cost', 'Domestic Shipping P2 Surcharge',
								'Domestic Shipping P3 Cost', 'Domestic Shipping P3 Additional Cost', 'Domestic Shipping P3 Surcharge', 'Domestic Shipping P4 Cost',
								'Domestic Shipping P4 Additional Cost', 'Domestic Shipping P4 Surcharge', 'International Shipping P1 Cost', 'International Shipping P1 Additional Cost',
								'International Shipping P1 Surcharge', 'International Shipping P2 Cost', 'International Shipping P2 Additional Cost', 'International Shipping P2 Surcharge',
								'International Shipping P3 Cost', 'International Shipping P3 Additional Cost', 'International Shipping P3 Surcharge', 'International Shipping P4 Cost',
								'International Shipping P4 Additional Cost', 'International Shipping P4 Surcharge', 'International Shipping P5 Cost', 'International Shipping P5 Additional Cost',
								'International Shipping P5 Surcharge', 'TemplateName', 'CustomFields', 'Eligible For EbayPlus'
									
								]
							)
	for enumerate,row in base_data.iterrows():
		if base_data.SKU[enumerate] in top_product.values and base_data.SKU[enumerate] not in sku_list:
			sku_list.append(base_data.SKU[enumerate])
			counter+=1
			newData=[]
			newData = [
			base_data['SKU'][enumerate],
			base_data['Localized For'][enumerate],
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			base_data['Product_Desc'][enumerate],
			'',
			base_data['Product_Description'][enumerate],
			'',
			'',
			base_data['URL_0'][enumerate],
			base_data['URL_1'][enumerate],
			base_data['URL_2'][enumerate],
			base_data['URL_3'][enumerate],
			base_data['URL_4'][enumerate],
			base_data['URL_5'][enumerate],
			base_data['URL_6'][enumerate],
			base_data['URL_7'][enumerate],
			base_data['URL_8'][enumerate],
			base_data['URL_9'][enumerate],
			base_data['URL_10'][enumerate],
			base_data['URL_11'][enumerate],
			'',
			'',
			'',
			'',
			base_data['TitleAdjusted'][enumerate],
			'',
			base_data['TQ - 0'][enumerate],
			base_data['TA - 0'][enumerate],
			base_data['TQ - 1'][enumerate],
			base_data['TA - 1'][enumerate],
			base_data['TQ - 2'][enumerate],
			base_data['TA - 2'][enumerate],
			base_data['TQ - 3'][enumerate],
			base_data['TA - 3'][enumerate],
			base_data['TQ - 4'][enumerate],
			base_data['TA - 4'][enumerate],
			base_data['TQ - 5'][enumerate],
			base_data['TA - 5'][enumerate],
			base_data['TQ - 6'][enumerate],
			base_data['TA - 6'][enumerate],
			base_data['TQ - 7'][enumerate],
			base_data['TA - 7'][enumerate],
			base_data['TQ - 8'][enumerate],
			base_data['TA - 8'][enumerate],
			base_data['TQ - 9'][enumerate],
			base_data['TA - 9'][enumerate],
			base_data['TQ - 10'][enumerate],
			base_data['TA - 10'][enumerate],
			base_data['TQ - 11'][enumerate],
			base_data['TA - 11'][enumerate],
			base_data['TQ - 12'][enumerate],
			base_data['TA - 12'][enumerate],
			base_data['TQ - 13'][enumerate],
			base_data['TA - 13'][enumerate],
			base_data['TQ - 14'][enumerate],
			base_data['TA - 14'][enumerate],
			base_data['TQ - 15'][enumerate],
			base_data['TA - 15'][enumerate],
			base_data['TQ - 16'][enumerate],
			base_data['TA - 16'][enumerate],
			base_data['TQ - 17'][enumerate],
			base_data['TA - 17'][enumerate],
			base_data['TQ - 18'][enumerate],
			base_data['TA - 18'][enumerate],
			base_data['TQ - 19'][enumerate],
			base_data['TA - 19'][enumerate],
			base_data['TQ - 20'][enumerate],
			base_data['TA - 20'][enumerate],
			base_data['TQ - 21'][enumerate],
			base_data['TA - 21'][enumerate],
			base_data['TQ - 22'][enumerate],
			base_data['TA - 22'][enumerate],
			base_data['TQ - 23'][enumerate],
			base_data['TA - 23'][enumerate],
			base_data['TQ - 24'][enumerate],
			base_data['TA - 24'][enumerate],
			base_data['Condition'][enumerate],
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			base_data['Quantity'][enumerate],
			base_data['Channel ID'][enumerate],
			base_data['Category'][enumerate],
			base_data['Shipping Policy'][enumerate],
			base_data['Payment Policy'][enumerate],
			base_data['Return Policy'][enumerate],
			base_data['List Price'][enumerate],
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			'',
			]



			
			tempdf.loc[len(tempdf)]=newData
		else:
			pass
	
	return tempdf.to_csv(EBAY_OUTPUT_FILE_NAME)

def RunFullModel():
	
	if New_ASIN_Load==1:
		print("Getting New ASINS")	
		data=GetAllAsins(ASIN_LOCATION+"\\"+LINKS_FILE)
		sleep(10)

	if Amazon_Data==1:
		print("Preparing for Scraping")	
		ExtractAmazonData(ASIN_LOCATION+"\\"+ASIN_OUTPUT_FILE)
		print("Scrapping Complete")

	if Data_Cleanse==1:
		print("Preparing for Data Cleansing")	
		FinalCleanups_v2()		#File Required ---- "final.csv", File produced --> "cleansed.csv"
		print("Data Cleansing Completed")

	if Ebay_Export==1:
		print("Preparing for EBAY Export")
		PrepareforEbayExport()		#File Required ---- "cleansed.csv", File produced --> "ebay_export_step_1.csv"
		print("Ebay Export Completed")

	if Ebay_Data_Cleanse==1:
		print("Cleansing the Cleansed Data for EBAY ") #File Required ---- "ebay_export_step_1.csv", File produced --> "automatedexport.csv"
		Attribute_Adjustments(file_name=EBAY_OUTPUT_FILE_NAME)

if __name__=="__main__":
	RunFullModel()