#### Selection of Products for Listing Algorithm #####

"""
STEP 1

1- CREATE AN INVERSE OF PRODUCT MAJOR RANK
2- CREATE AN INVERSE OF PRODUCT CATEGORY RANK
3- SUM 1 AND 2
4- BASED ON 3 SORT ALL THE PRODUCTS
5 - EXPORT THE LIST

STEP 2

1- SORT THE TOP PRODUCTS BY RANKS

"""

### DECLARE LIBRARIES

import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import datetime

# Constraints 
MAX_INVENTORY_VAL=130000				
MAX_PRODUCT_COUNT=2000
BUFFER_SALES=1000

#RANKING IMPORTANCE
MAJOR_RANKS_WEIGHT=10
SUB_MAJOR_RANKS_WEIGHT=5
RATINGS_WEIGHT=5

#FLAGS
EXCLUDE_DISCOUNTINUED_PRODUCTS=True
EXCLUDE_PRODUCTS_WITHOUT_RATINGS=True

#VARIABLES
DATA_FILE='Updated1.csv'

def load_csv():
	df=pd.read_csv(DATA_FILE)
	df_new=df[['SKU','Major_Rank','Sub_Rank','Stars_','Ratings','List Price','Quantity']]
#	distinct_count_cat_items=df_new.groupby('Category')['SKU'].nunique()
	df_new.drop_duplicates(subset=['SKU'],inplace=True)
	return df_new

def Cleanups():
	df_new=load_csv()

	#Get MajorRank
	def Major_Ranking_Cleanup_Process(mystr):
		try:
			newstr=mystr.find(" in ")
			return mystr[:newstr]
		except:
			return None

	def Sub_Ranking_Cleanup_Process(mystr):
		try:
			newstr=mystr.find(" in ")
			return mystr[:newstr]
		except:
			return None
	
	def Ratings_Cleanup_Process(mystr):
		try:
			newstr=mystr.find(" ratings")
			return mystr[:newstr]
		except:
			return None



	df_new["Major_Ranks_Adjusted"]=df_new['Major_Rank'].apply(Major_Ranking_Cleanup_Process)
	df_new["Sub_Ranks_Adjusted"]=df_new['Sub_Rank'].apply(Sub_Ranking_Cleanup_Process)
	df_new["Ratings_Adjusted"]=df_new['Ratings'].apply(Ratings_Cleanup_Process)

	return df_new

def Cleanups_step2():
	#This will exclude the ones which have been failed to clear up#
	df=Cleanups()
	df_new=df[df['Sub_Rank'].notnull()]
	df_new_1=df_new[df_new['Ratings_Adjusted']!="1 ratin"]
	print(f"Based on the cleanups we have dropped {df.shape[0]-df_new_1.shape[0]} values which had incorrect positions")
	return df_new_1

def Inverse_Calculations():
	df=Cleanups_step2()
	def Calculate_Inverse(x):
		if x is None:
			return 0
		if x.find(",")>0:
			temp_val=x.replace(",","")
			val=float(temp_val)
		else:
			val=float(x)
		
		final_inverse=(1/val)
		return final_inverse

	df['Inverse_Major_Ranks']=df['Major_Ranks_Adjusted'].apply(Calculate_Inverse)
	df['Inverse_Sub_Ranks']=df['Sub_Ranks_Adjusted'].apply(Calculate_Inverse)

	return df

def ApplyWeights():
	df=Inverse_Calculations()
	def Apply_Weight_Major_Ranks(x):
		if x is None:
			return 0
		
		return x*MAJOR_RANKS_WEIGHT
	def Apply_Weight_Sub_Major__Ranks(x):
		if x is None:
			return 0
		return x*SUB_MAJOR_RANKS_WEIGHT
	def Apply_Weight_Ratings_Ranks(x):
		if x is None:
			return 0
		return x*RATINGS_WEIGHT
		
	df['Major_Rank_Weight_Applied']=df['Inverse_Major_Ranks'].apply(Apply_Weight_Major_Ranks)
	df['Sub_Major_Rank_Weight_Applied']=df['Inverse_Sub_Ranks'].apply(Apply_Weight_Sub_Major__Ranks)
	df['Collective_Weights']=df['Major_Rank_Weight_Applied']+df['Sub_Major_Rank_Weight_Applied']

	return df

def Sort_Data():
	df=ApplyWeights()
	sorted_df=df.sort_values(by=['Collective_Weights'],ascending=False)
	top_df=sorted_df.head(MAX_PRODUCT_COUNT)
	return top_df.to_csv('Top_products.csv')

