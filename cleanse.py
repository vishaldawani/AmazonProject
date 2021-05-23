## THIS CLEANSES THE OUTPUT FROM SCRAPPED AMAZON DATA
## NEXT STEP IS TO USE THIS INFORMATION AND UPDATE THE EBAY 

import pandas as pd
import numpy as np
import re 
import os
import sys
import itertools
import math

PIC_COLS=100
files_dir=os.listdir(os.getcwd())
BASE_PRICE=0
MAX_PRICE=400
MAX_MIN_PRICE_RANGE=1						#1 DICTATES PICK MAXIMUM
FILE_NAME="final.csv"
MARGIN=0.3									# 30% MARGIN

def load_file():
	#Load the dataframe
	required_file=[file for file in files_dir if file.endswith('csv') and file==FILE_NAME]
	if required_file is not None:
		for file in required_file:
			temp_df=pd.read_csv(file,sep=",",index_col='SKU')
			return temp_df

def AdjustBrandTitle():
	tempdf=load_file()
	print("Extracting Brand Titles...")
	tempdf.reset_index(inplace=True)	
	working_col=tempdf['Brand/Title']
	col_to_drop=['Brand/Title']
	brand_list=[]
	for row in working_col:
		word=str(row)
		if word.find('Visit',0)==0:
			word=word.replace('Visit the ','')
			word=word.replace('Store','')
			word=word.replace(' ','')
		else:
			word=word.replace('Brand: ','')
		word=word.upper()
		brand_list.append(word)
	tempdf['TitleAdjusted']=pd.DataFrame(brand_list,columns=['New Brand'])
	tempdf.drop(columns=col_to_drop,inplace=True)
	return tempdf

def ExtractImages(pic_columns=PIC_COLS,delimiter_="|"):

	tempdf=AdjustBrandTitle()
	print("Extracting Images...")
	tempdf.reset_index(inplace=True)
	
	temp_clean_csv_non_formatted=tempdf['Pic_URL'].str.split(delimiter_,expand=True)
	temp_clean_csv_non_formatted_temp=temp_clean_csv_non_formatted.copy()

	total_rows=temp_clean_csv_non_formatted.shape[0]
	total_cols=temp_clean_csv_non_formatted.shape[1]

	# Adjust the Image DataFrame Swapping Issues
	for row in range(total_rows):
		update_counter=0
		max_col=temp_clean_csv_non_formatted.iloc[row].count()-2
		if max_col==0 or max_col is None:
			pass
		else:
			#Start from the last_col
			for start_num in  range(max_col,-1,-1):
				url_update=temp_clean_csv_non_formatted_temp.iloc[row][start_num]
				temp_clean_csv_non_formatted.iloc[row][update_counter]=url_update
				update_counter+=1

    # Adjust the JPG's Issues	
	for row in range(total_rows):
		for col in range(total_cols):
			if temp_clean_csv_non_formatted.iloc[row][col] is None or pd.isna(temp_clean_csv_non_formatted.iloc[row][col]) or (len(temp_clean_csv_non_formatted.iloc[row][col])==0):
				pass
			else:
				temp_text=str(temp_clean_csv_non_formatted.iloc[row][col])
				temp_text_loc=temp_text.find("._AC_")

				if temp_text.endswith(".jpg"):
					pass
				else:
					base_str=temp_text[temp_text_loc:]
					left_side=base_str[:12]
					middle_side=".jpg"
					first_update=left_side+middle_side
					updated_string=temp_text[:temp_text_loc]+first_update
					temp_clean_csv_non_formatted.iloc[row][col]=updated_string

	new_df=tempdf.join(temp_clean_csv_non_formatted,how='inner')
	col_names=[col for col in new_df.columns]
	adjusted_col=[]
	counter=0
	for col in col_names:
		if isinstance(col, int):
			adjusted_col.append(f"URL_{counter}")
			counter+=1
		else:
			adjusted_col.append(col)
	new_df.columns=adjusted_col
	return new_df

def TechnicalInformation():
	tempdf=ExtractImages()
	print("Cleansing Technical Information")
	temp_clean_csv=tempdf['Technical'].str.split('\n',expand=True)
	arr=np.arange(len(temp_clean_csv.columns))%2
	temp_df_c=temp_clean_csv.iloc[:,arr==0]
	new_df=pd.DataFrame()
	for index,row in temp_df_c.iterrows():
		counter=0
		for item in row:
			try:
				if item is not None and len(item)>0:
					counter+=1
			except:
				pass
			start_len=counter
		row_counter=0
		questions_range=0
		answers_range=counter
		questions_list=[]
		answers_list=[]
		place_holder_list=[]
		for i in range(int(start_len/2)):
			questions_list.append(temp_df_c.iloc[index][questions_range])
			answers_list.append(temp_df_c.iloc[index][answers_range])
			answers_range+=2
			questions_range+=2
		mega_list=list(zip(questions_list,answers_list))
		out=list(itertools.chain(*mega_list))
		a_series=pd.Series(out)
		new_df=new_df.append(a_series,ignore_index=True)
		#print("Index Loading "+str(index))

	tempdf=tempdf.join(new_df,how='outer')
	# Adjust the Column Names to represent the questions and answers
	adjusted_col=[]
	question_num=0
	answer_num=0
	col_names=[col for col in tempdf.columns]
	for col in col_names:
		if isinstance(col, int):
			if col %2 ==0:
				adjusted_col.append(f"TQ - {question_num}")
				question_num+=1
			else:
				adjusted_col.append(f"TA - {answer_num}")
				answer_num+=1
		else:
			adjusted_col.append(col)
	tempdf.columns=adjusted_col
	return tempdf

def AdditionalInformation():
	tempdf=TechnicalInformation()
	print("Extracting Additional Information...")
	required_df=pd.DataFrame(columns={1,2,3,4})
	temp_clean_csv=tempdf['Additional'].str.rsplit('\n\n\n\n||',expand=True)
	rankings_df=temp_clean_csv[0].str.split('\n\n',expand=True)

	major_ranks="" # column 1 --Column 
	sub_ranks="" # Column 2
	starss="" # Column 6,7,8
	ratingss=""

	for index,col in rankings_df.iterrows():
		try:
			major_ranks=col[1]
		except:
			major_ranks="NULL"
		try:
			sub_ranks=col[2]
		except:
			sub_ranks="NULL"

		try:
		#STARS
			if len(col[6])>0:
				starss=col[6]
			elif len(col[7])>0:
				starss=col[7]
			else:
				starss=col[8]
			starss=starss.strip('\n')
		except:
			starss="NULL"

		#RATINGS
		try:
			if len(col[10])>0:
				ratingss=col[10]
			elif len(col[11])>0:
				ratingss=col[11]
			else:
				ratingss=col[12]
			ratingss=ratingss.strip('\n')
		except:
			ratingss="NULL"
		
		newdf=[]
		newdf=[major_ranks,sub_ranks,starss,ratingss]
		required_df.loc[len(required_df)]=newdf
		major_ranks="" # column 1 --Column 
		sub_ranks="" # Column 2
		starss="" # Column 6,7,8
		ratingss=""
	
	required_df.rename(columns={1:"Major_Rank",2:"Sub_Rank",3:"Stars_",4:"Ratings"},inplace=True)
	combined_df=tempdf.join(required_df,how='inner')
	return combined_df

def PriceFilter():
	df=AdditionalInformation()
	print("Applying a Price Filter")
	tempdf=df['List Price']
	price_list=[]

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
	
	for row in tempdf:
		temp_price=str(row)
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
		price_list.append(round(prices_new,2))

	# Add another Price Filter

	df['New_Prices']=pd.DataFrame(price_list)
	df['New_Prices']=df[
						(df['New_Prices']<MAX_PRICE)&(df['New_Prices']>BASE_PRICE)

					]['New_Prices']

	filteredf=df[df['New_Prices'].notnull()]
	return filteredf

def QuantityFilter():
	df=PriceFilter()
	print("Applying a Quantity Filter")	
	df['Quantity_Updated']=np.where(df['Quantity']>0,1,0)
	return df

def Adjustments():
	df=QuantityFilter()
	print("First layer of Adjustments")
	cols=['index','Unnamed: 0','List Price','Pic_URL','Quantity']
	if isinstance(df, pd.DataFrame):
		pass
	else:
		return None

	#Delete repeated columns
	tempdf=df.copy()
	tempdf.drop([col for col in tempdf.columns if col in cols], axis=1, inplace=True)
	tempdf.rename(columns={'New_Prices':'List Price','Quantity_Updated':'Quantity'},inplace=True)
	return tempdf

def FinalCleanups_v1():
	df=Adjustments()
	print("Second layer of Adjustments")
	df_new=df[df.Additional!="----"]
	return df_new

def FinalCleanups_v2():
	df=FinalCleanups_v1()
	print("Final Tweaks...")
	df=df[df.Major_Rank.notnull()]
	if isinstance(df, pd.DataFrame):
		print(f"Total Rows {df.shape[0]}")
	else:
		return None

	return df.to_csv("cleansed.csv")

