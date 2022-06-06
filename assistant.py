from msilib import type_binary
import pandas as pd
from io import StringIO
import requests
import pymongo
import numpy as np
from selenium import webdriver
import time

client = pymongo.MongoClient("localhost", 27017)
eftManege = client['eftManege']



def getNev(typen,url):
    if typen=='A':
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.get(url)
        nevEbtal = ''
        dateNev = ''
        while nevEbtal == '' or dateNev == '':
            nevEbtal = driver.find_element_by_css_selector('#PRedTran').text
            dateNev = driver.find_element_by_css_selector('#NAVDate').text
            time.sleep(2)

        nevEbtal = int(nevEbtal.replace(',',''))
        dateNev = dateNev.split(' ')[0].split('/')
        if len(dateNev[1])==1 and len(dateNev[2])==1:
            dateNev = dateNev[0] + '0' + dateNev[1] + '0' + dateNev[2]
        elif len(dateNev[1])==1 and len(dateNev[2])>1:
            dateNev = dateNev[0] + '0' + dateNev[1] + dateNev[2]
        elif len(dateNev[1])>=1 and len(dateNev[2])==1:
            dateNev = dateNev[0] + dateNev[1] + '0' + dateNev[2]
        else:
            dateNev = dateNev[0] +  dateNev[1] +  dateNev[2]
        dateNev = int(dateNev)

        return [nevEbtal, dateNev]

def gregorian_to_jalali(GDate):
    GDate = str(GDate)
    gy = int(GDate[:4])
    gm = int(GDate[4:6])
    gd = int(GDate[6:])
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gm > 2):
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if (days > 365):
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if (days < 186):
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    if len(str(jm))==1:
        jm = '0'+str(jm)
    if len(str(jd))==1:
        jd = '0'+str(jd)
    JDate = str(jy)+str(jm)+str(jd)
    JDate = int(JDate)
    return JDate


def histori_Update():
    dff = pd.DataFrame(khatamDb.find_one(sort=[("<DTYYYYMMDD>", pymongo.DESCENDING)]))
    Last_update = dff['<DTYYYYMMDD>'].max()
    df = StringIO(requests.get(url='http://www.tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i=18865325633315847').text)
    df = pd.read_csv(df,sep=",")
    df['<DTYYYYMMDD>'] = [gregorian_to_jalali(x) for x in df['<DTYYYYMMDD>']]
    df = df[df['<DTYYYYMMDD>']>Last_update]
    if len(df)>0:
        dff = dff.append(df)

    dff.to_excel('Data/histori.xlsx')

#این تابع صرفا برای ایجاد صندوق جدید مورد استفاده قرار میگیرد
def newEtf(urlStart,name,urlNev,TypeSite):
    '''
    urlStart: لینک تابلو tse
    name: نماد صندوق اختصار
    urlNev: ادرسی که nev ابطال به صورت دقیق درج شده باشد
    TypeSite: اگر nev ابطال در tse باشد نوع A
    '''
    infoEtfDb =  eftManege['infoEtfDb']
    try:already = len(dict(infoEtfDb.find_one({'name':name})))==0
    except:already = True
    if already:
        print('create Etf')
        infoEtfDb.insert_one({'name':name, 'url':urlStart, 'urlNev':urlNev, 'site':TypeSite})
        df = StringIO(requests.get(url=urlStart).text)
        df = pd.read_csv(df,sep=",")
        df['<DTYYYYMMDD>'] = df['<DTYYYYMMDD>'] = [gregorian_to_jalali(x) for x in df['<DTYYYYMMDD>']]
        df['nav'] = np.nan
        df = df.to_dict(orient='records')
        newEtfDb = eftManege[name]
        newEtfDb.insert_many(df)
        print('set Etf')
    else:
        print('STOP, Etf is already')

def updateEtf(name):
    EtfDb = eftManege[name]
    lastUpdate = EtfDb.find_one(sort=[('<DTYYYYMMDD>', pymongo.DESCENDING)])['<DTYYYYMMDD>']
    etfinfo = eftManege['infoEtfDb'].find_one({'name':name})
    url = etfinfo['url']
    typn = etfinfo['site']
    urlnev = etfinfo['urlNev']
    df = pd.read_csv(StringIO(requests.get(url=url).text),sep=",")
    df['<DTYYYYMMDD>'] = [gregorian_to_jalali(x) for x in df['<DTYYYYMMDD>']]
    df = df[df['<DTYYYYMMDD>']>lastUpdate]

    if len(df)>0:
        nav = getNev(typn,urlnev)
        print(nav)
        df['nav'] = np.nan
        df = df.set_index('<DTYYYYMMDD>')
        df['nav'][nav[1]] = nav[0]
        print(df)
        df = df.reset_index()
        df = df.to_dict(orient='records')
        EtfDb.insert_many(df)
        print('Update')
    else:
        print('Updated')

def listEtf():
    listEtf = []
    for x in eftManege['infoEtfDb'].find():
        listEtf.append(x['name'])
    return listEtf