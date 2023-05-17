from urllib.request import Request, urlopen, urlretrieve
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.uvek-gis.admin.ch/BFE/ogd/staging/'

def read_url(url):

    csvList = []

    url = url.replace(" ","%20")
    req = Request(url)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    for i in x:
        file_name = i.extract().get_text()
        if '.csv' in file_name:
          csvList.append(file_name)

    df = pd.DataFrame(csvList, columns= ['test0'])
    df.to_csv('files/fileNames.csv')

read_url(url)
