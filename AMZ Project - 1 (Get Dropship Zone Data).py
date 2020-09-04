
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from time import sleep
import sys

CHROME_LOCATION="C:\\Users\\Vishal.Dawani\\Dropbox (Onsite)\\9.0 Pricing Analysis and Reporting\\3.Automation\\ChromeDriver\\chromedriver.exe"
REPORT_LINK="https://www.dropshipzone.com.au/customer/account/login/"
LINKS=["https://www.dropshipzone.com.au/photofast-aircharge-qi-compatible-10w-fast-charge-sku-ac8000.html","https://www.dropshipzone.com.au/electronics/ugreen-mobile-waterproof-bag-black-60959.html"
,"https://www.dropshipzone.com.au/electronics/sandisk-ixpand-imini-flash-drive-sdix40n-16gb-grey-ios-usb-3-0.html"]

USERNAME="yashdawani386@gmail.com"
PASSWORD="Qwerty123*"


class DownloadStockData:
	def __init__(self):
		pass
	def deletePrevious():
		pass
	def checkFornEw():
		pass
	def masterInventoryList():
		pass

	def PostToAccess():
		pass

	def DownloadPricingReport(UserName=USERNAME,Password=PASSWORD,report_link=REPORT_LINK,chrome_path=CHROME_LOCATION):
			ChromePath=CHROME_LOCATION
			options = webdriver.ChromeOptions()
			options.add_experimental_option('useAutomationExtension', False)
			driver= webdriver.Chrome(options=options,executable_path=chrome_path)
			driver.set_window_position(0,0)
			driver.get(report_link)
			try:
				target_Email=driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div/form/div[1]/div[1]/div/ul/li[1]/div/input")
				target_Email.send_keys(UserName)
				target_password=driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div/form/div[1]/div[1]/div/ul/li[2]/div/input")
				target_password.send_keys(Password)
				enter_website=driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div/form/div[2]/div[1]/div/button")
				enter_website.click()

			except:
				print ("Incorrect Credentials")
				driver.quit()

			sleep(5)
			for link in LINKS:
				if link is not None:
					driver.get(link)

			sleep(5)

			driver.quit()

DownloadPricingReport(UserName=USERNAME, Password=PASSWORD)