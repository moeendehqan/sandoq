
from selenium import webdriver
from io import StringIO
import requests
import pandas as pd
import assistant as ast
driver = webdriver.Chrome(executable_path='chromedriver.exe')

driver.get('http://etf.isatispm.com/')
nevEbtal = driver.find_element_by_css_selector('#Live_SellNAVPerShare').text
nevEbtal = int(nevEbtal.split(' ')[0].replace(',',''))
date = driver.find_element_by_css_selector('#Live_JalaliDate').text
date = int(date.split(' ')[1].replace('/',''))


print(df)
