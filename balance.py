import requestsi
from bs4 import BeautifulSoup
import pandas as pd
import threading

def get_balance(hisse):
    url = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse=" + hisse
    r = requests.get(url)
    s = BeautifulSoup(r.text,"html.parser")
    select1 = s.find("select", id="ddlMaliTabloFirst")
    select2 = s.find("select", id="ddlMaliTabloGroup")

    dates = []
    dates1 = []
    years = []
    quarters = []
    alldata = []

    cocuklar = select1.findChildren("option")
    grup = select2.findChild("option")["value"]

    for i in cocuklar:
        dates.append(i.string.rsplit("/"))
        dates1.append(i.string)

    dates1 = pd.to_datetime(dates1, format="mixed").strftime('%m/%Y')

    plus = 0
    while len(dates)%4!=0:
        plus += 1
        dates.append([0,0])

    for i in range(0,len(dates),4):
        parametreler = (
            ("companyCode", hisse),
            ("exchange", "TRY"),
            ("financialGroup", grup),
            ("year1",dates[i][0]),
            ("period1",dates[i][1]),
            ("year2",dates[i+1][0]),
            ("period2",dates[i+1][1]),
            ("year3",dates[i+2][0]),
            ("period3" ,dates[i+2][1]),
            ("year4",dates[i+3][0]),
            ("period4",dates[i+3][1])
        )
        print(f"{hisse}: {dates[i:i+4]}")
        url2 = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
        r2 = requests.get(url2, params=parametreler).json()["value"]
        data = pd.DataFrame.from_dict(r2)
        columns = data['itemCode']
        columns.name = "index"
        data = data.drop(["itemCode","itemDescTr","itemDescEng"], axis=1)
        data = data.set_index(columns)
        
        if len(dates)-i==4 and plus!=0:
            data = data.iloc[:,:4-plus]
        alldata.append(data)

    alldata = pd.concat(alldata, axis=1)
    alldata = alldata.fillna(0)
    alldata = alldata.astype('int')

    alldata.columns = dates1

    alldata.to_excel("{}.xlsx".format(hisse))


def main():
    stocks = ["THYAO","ASELS"]
    for stock in stocks:
        t = threading.Thread(target=get_balance, args=(stock,))
        t.start()


if __name__ == "__main__":
    main()
