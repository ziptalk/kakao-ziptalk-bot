# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urlencode, quote_plus
from urllib.request import Request, urlopen
from openpyxl import load_workbook
from bs4 import BeautifulSoup
import bs4
from lxml import html
import numpy as np
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate('ziptalk-chatbot-firebase-adminsdk-kz477-4cadf62941.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'ziptalk-chatbot.appspot.com'
})

bucket = storage.bucket()

now = datetime.now()

# bucket_name = "ziptalk-chatbot"

file_name = "11410_남가좌동_DMC파크뷰자이1단지_202106_savefig.png"

# imageBlob = bucket.blob("/")
# imagePath = "./"+file_name
# imageBlob = bucket.blob(file_name)
# imageBlob.download_to_filename(file_name)

print(
    "Blob {} downloaded to {}.".format(
            "/", file_name
        )
)

url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade'
service_key = 'PdWFVj9WjaMQ7Qmoamq2n1f81jXwnfinEaCxcbGTtjmlmpwPcfEsQkky9Cdgz6J+tWUeGpU5BaVi6fZsgnL9qw=='  # 서비스 인증키

res = urlopen(url)
print(res.status)  ## 200

time_code_list =  []

for i in range(0, 36):
    time = now - relativedelta(months=i)
    time = time.strftime("%Y%m")
    time_code_list.append(time)

time_code_list.reverse()
print(time_code_list)

wb = load_workbook(filename='dongcode_20180703_real.xlsx')
sheet = wb['Sheet1']

do_city_list = []
do_city_json = []

for i in range(1, 230):
    dic = {"label" : sheet[i][2].value, "action": "message", "messageText" : sheet[i][2].value}
    do_city_list.append(sheet[i][2].value)

do_city_set = set(do_city_list)
do_city_list = list(do_city_set)

# print(do_city_list)

for do_city in do_city_list:
    dic = {"label" : do_city, "action": "message", "messageText" : do_city}
    do_city_json.append(dic)

print(do_city_json)

do_city_name = input("도(특별자치도) 혹은 시(특별시, 광역시)를 입력하세요. :: ")

si_gun_gu_list = []
si_gun_gu_json = []

for i in range(1, 230):
    # for i in range(1, 18858):
    if (do_city_name[0:2] in sheet[i][2].value):
        si_gun_gu_list.append(sheet[i][3].value)

print(si_gun_gu_list)

si_gun_gu_name = input("시/군/구 를 입력하세요. :: ")
area_name = input("읍/면/동/리 를 입력하세요. :: ")

dongcode = " "
search_code = " "

for i in range(1, 230):
    # for i in range(1, 18858):
    if (do_city_name[0:2] in sheet[i][2].value) and (si_gun_gu_name in sheet[i][3].value):
        dongcode = sheet[i][1].value
        break

if dongcode == " ":
    print("dongcode error")

else:
    # 동코드가 1111010100 이런 형식이므로 앞에 11110 만 가져오도록 인덱싱.
    search_code = dongcode[0:5]
    print("검색코드" + search_code)

queryParams = '?' + urlencode(
            {
                quote_plus('ServiceKey'): service_key,
                quote_plus('LAWD_CD'): search_code,
                quote_plus('DEAL_YMD'): 202104
            }
        )

request = Request(url + queryParams)
request.get_method = lambda: 'GET'
response_body = urlopen(request).read()

result_body = response_body.decode('utf-8')

try:
    try:
        xmlobj = bs4.BeautifulSoup(result_body, 'lxml-xml')
    except:
        print("bs4 오류")

    try:
        rows = xmlobj.findAll('item')
    except:
        print("xmlobj 오류")

    columns = rows[0].find_all()

    rowList = []
    nameList = []
    columnList = []
    result = ''
    apt_list = []
    dong_list = []

    rowsLen = len(rows)

    try:
        for i in range(1, rowsLen):
            columns = rows[i].find_all()
            columnsLen = len(columns)

            for j in range(0, columnsLen):
                

                if i == 0:
                    nameList.append(columns[j].name)
                else:
                    dong_temp = columns[3].text.replace(' ', '')
                    dong_list.append(dong_temp)
                    if columns[3].text == (' ' + area_name): # 동이름이 같으면
                        result = result + columns[j].name + \
                            ' : ' + columns[j].text + '\n'
                        if columns[j].name == '아파트':
                            apt_list.append(columns[j].text)

                eachColumn = columns[j].text
                columnList.append(eachColumn)

            if columns[3].text == (' ' + area_name):
                result = result + '\n---------------------\n'

            rowList.append(columnList)
            columnList = []

        # print(result)
        apt_set = set(apt_list) #중복제거
        apt_list = list(apt_set)

        dong_set = set(dong_list)
        dong_list = list(dong_set)
        print(dong_list)
        print(apt_list)
    except:
        print("result 오류")

except:
    print("get_act_apt_parsing_pd 함수 오류 발생")

apt_name = input("아파트명을 입력하세요. :: ")
price_list = []
graph_list = []

for time_code in time_code_list:

    apt_price = ''

    queryParams = '?' + urlencode(
                {
                    quote_plus('ServiceKey'): service_key,
                    quote_plus('LAWD_CD'): search_code,
                    quote_plus('DEAL_YMD'): int(time_code)
                }
            )

    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()

    result_body = response_body.decode('utf-8')
    try:
        try:
            xmlobj = bs4.BeautifulSoup(result_body, 'lxml-xml')
        except:
            print("bs4 오류")

        try:
            rows = xmlobj.findAll('item')
        except:
            print("xmlobj 오류")

        columns = rows[0].find_all()

        rowList = []
        nameList = []
        columnList = []
        result = ''
        apt_list = []
        price_info = []

        rowsLen = len(rows)

        try:
            for i in range(1, rowsLen):
                columns = rows[i].find_all()
                columnsLen = len(columns)

                for j in range(0, columnsLen):
                    if i == 0:
                        nameList.append(columns[j].name)
                    else:
                        if columns[3].text == (' ' + area_name): # 동이름이 같으면
                            result = result + columns[j].name + \
                                ' : ' + columns[j].text + '\n'
                            if apt_name in columns[4].text: # 아파트명이 같으면
                                # price_list.append(columns[0].text)
                                apt_name = columns[4].text
                                apt_price = columns[0].text
                                # print(apt_price)

                    eachColumn = columns[j].text
                    columnList.append(eachColumn)

                if columns[3].text == (' ' + area_name):
                    result = result + '\n---------------------\n'

                rowList.append(columnList)
                columnList = []

            apt_price = apt_price.replace(' ', '')
            apt_price = apt_price.replace(',', '')
            print(apt_price)
            price_info = [time_code, int(apt_price)]
            graph_list.append(tuple(price_info))

        except:
            print("result 오류")

    except:
        print("get_act_apt_parsing_pd 함수 오류 발생")

print(graph_list)

x, y = zip(*graph_list)

# plt.step(x, y)
plt.plot(x, y)
plt.xticks(rotation=45)
file_name = str(search_code) + '_' + area_name + '_' + apt_name + '_' + str(time_code_list[-1]) + '_' + 'savefig.png'
plt.savefig(file_name)
# plt.show()
imageBlob = bucket.blob("/")
imagePath = "./"+file_name
imageBlob = bucket.blob(file_name)

imageBlob.upload_from_filename(imagePath)
imageBlob.make_public()
print(imageBlob.public_url)


