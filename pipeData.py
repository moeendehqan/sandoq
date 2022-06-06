
import time
import assistant as ass



while True:
    h = time.localtime().tm_hour
    m = time.localtime().tm_min
    if m == 00 and h ==16:
        listEtf = ass.listEtf()
        for x in listEtf:
            ass.updateEtf(x)
        time.sleep(120)
