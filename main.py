
import requests     # 2.18.4
import json         # 2.0.9
import pandas as pd # 0.23.0
import numpy as np
import time
import os
import frictionless
import ast
import re
from urllib.request import Request, urlopen, urlretrieve
from bs4 import BeautifulSoup

url = 'https://www.uvek-gis.admin.ch/BFE/ogd/staging/'

def extract_id(fileName):
    ogd_id = fileName.partition('_')[0]
    return ogd_id.replace('ogd', '')

def getInformation(url):

  csvList = []
  url = url.replace(" ","%20")
  req = Request(url)
  a = urlopen(req).read()
  soup = BeautifulSoup(a, 'html.parser')
  x = (soup.find_all('a'))

  for elem in x:
    stringElem = str(elem)

    if 'csv' in stringElem:
      if 'ogd' in stringElem:
        fileName = re.search('href="(.*)"', stringElem).group(1)
        csvList.append([fileName, extract_id(fileName)])

  df = pd.DataFrame(csvList, columns= ['fileName', 'ogd_id'])
  print(df)
  return df

df = getInformation(url)

toDoList = []

staging = 'staging/'
url_ogd = 'https://www.uvek-gis.admin.ch/BFE/ogd/'
url = 'https://www.uvek-gis.admin.ch/BFE/'
dataPackage = 'datapackage.json'

for index, row in df.iterrows():

  # information --> what to do with the ID
  actionDict = {}

  # load original data package
  folderPath = url_ogd + row['ogd_id'] + '/'
  datapackagePath = os.path.join(folderPath, dataPackage)

  fileName = row['fileName']

  # new file path --> to staging folder
  stagingFilePath = url_ogd + 'staging/' + fileName

  # store the response of URL
  response = urlopen(datapackagePath)

  # storing the JSON response
  data_json = json.loads(response.read())

  print('original datapackage: ')
  print(data_json)


  # change source file
  jsonAsString = str(data_json)
  jsonAsString = jsonAsString.replace(os.path.join(folderPath, fileName), stagingFilePath)
  updatedJSON = ast.literal_eval(jsonAsString)

  #print('---------------------------')
  #print('adjusted datapackage: ')
  #print(updatedJSON)
  #print('===========================')

  # path for temporary datapackage
  tmpJSON_path = 'tmpPackage.json'

  # save the file as data.json
  with open(tmpJSON_path, 'w') as f:
    json.dump(updatedJSON, f)

  report = frictionless.validate(tmpJSON_path)

  actionDict['fileName'] = row['fileName']
  actionDict['origin'] = stagingFilePath


  if report.valid:
    print("Valid.\n")
    actionDict['action'] = 'replace'
    actionDict['destination'] = os.path.join(folderPath, dataPackage)

  else:
    print("Not valid!\n")
    actionDict['action'] = 'delete'
    actionDict['destination'] = '-'

  toDoList.append(actionDict)
