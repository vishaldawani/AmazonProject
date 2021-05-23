### The methods here will be used to update the fixes
import pandas as pd
import os
import numpy as np
import re


# Loading Filess

def load_file(file_name):
	files=os.listdir(os.getcwd())
	required_file=[file for file in files if file==file_name]
	if len(required_file)==0:
		raise Exception ("No file Found")
	df=pd.read_csv(os.getcwd()+'\\'+file_name)
	return df

#Product Descriptions
def Product_Descriptions(file_name):
	tempdf=load_file(file_name)
	proc_desc=tempdf['Product Description'] 
	tempdf['E'] = tempdf['Product Description'].map(lambda x: re.sub(r"[^a-zA-Z\n0-9]+", ' ', str(x)))
	tempdf['F'] = tempdf['E'].replace('\n\n\n','',regex=True)
	tempdf['New_Product_Descriptions'] = tempdf['F'].replace('\n','\n\n',regex=True)
	tempdf['Product Description']=tempdf['New_Product_Descriptions']
	tempdf.drop(columns=['E','F','New_Product_Descriptions'],inplace=True)
	return tempdf

#Product Descriptions
def Title_Reductions(file_name,char=80):
	tempdf=Product_Descriptions(file_name=file_name)
	tempdf['Reduced_Titles']=tempdf['Title'].map(lambda x: x.strip())
	tempdf['Reduced_Titles']=tempdf['Title'].map(lambda x: x[:char])
	tempdf['Title']=tempdf['Reduced_Titles']
	tempdf.drop(columns=['Reduced_Titles'],inplace=True)
	return tempdf

def CamelAdjustments(file_name):
	tempdf=Title_Reductions(file_name=file_name)
	tempdf['X']=tempdf['Title'].map(lambda x: x.title())
	tempdf['Title']=tempdf['X']
	tempdf.drop(columns=['X'],inplace=True)
	return tempdf

def Remove_Desc_product_Desc(file_name):
	tempdf=CamelAdjustments(file_name=file_name)
	tempdf['E'] = tempdf['Product Description'].map(lambda x: x.replace('This fits your \n\n Enter your model number\n\nto make sure this fits \n\n\n\n',' '))
	tempdf['Product Description']=tempdf['E']
	tempdf.drop(columns=['E'],inplace=True)
	return tempdf

def Attribute_Adjustments(file_name):
	tempdf=Remove_Desc_product_Desc(file_name=file_name)
	#Attribute_1 Enhancement
	tempdf['Attribute Name 1']='Brand'
	tempdf['Attribute Value 1']=tempdf['Brand']
	tempdf['Attribute Name 2']='Colour'
	tempdf['Attribute Value 2']='Refer to Product Picture'
	tempdf['Attribute Name 3']='Type'
	tempdf['Attribute Value 3']=tempdf['Category']
	tempdf['Brand']=''
	tempdf.drop(columns=['Unnamed: 0'],inplace=True,axis=1)
	tempdf.to_csv("ebay_export_step_2.csv",index=False)
	return print("Export Completed")




	

