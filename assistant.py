import pandas as pd
from io import StringIO
import requests


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
    dff = pd.read_excel('Data/histori.xlsx').drop(columns='Unnamed: 0')
    Last_update = dff['<DTYYYYMMDD>'].max()
    if Last_update>15000000:
        dff['<DTYYYYMMDD>'] = [gregorian_to_jalali(x) for x in dff['<DTYYYYMMDD>']]
    dff = dff[dff['<DTYYYYMMDD>']<dff['<DTYYYYMMDD>'].max()]
    Last_update = dff['<DTYYYYMMDD>'].max()
    df = StringIO(requests.get(url='http://www.tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i=18865325633315847').text)
    df = pd.read_csv(df,sep=",")
    df['<DTYYYYMMDD>'] = [gregorian_to_jalali(x) for x in df['<DTYYYYMMDD>']]
    df = df[df['<DTYYYYMMDD>']>Last_update]
    if len(df)>0:
        dff = dff.append(df)

    dff.to_excel('Data/histori.xlsx')