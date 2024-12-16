import os
from fastapi import FastAPI
import requests
import json
import time
import pandas as pd
import fast_bitrix24
from fast_bitrix24 import BitrixAsync
import asyncio

URLBITRIX = os.environ['URLBITRIX']
URLSERVICE = os.environ['URLSERVICE']
LISTID = os.environ['LISTID']
ENVAUTH = os.environ['ENVAUTH']
REGUF = os.environ['REGUF']

regdict = dict()

def getlistregions():
    global regdict
    b =BitrixAsync(URLBITRIX)   
    print('get ID from list')
    listsdata = {
                'IBLOCK_ID':LISTID,
                'IBLOCK_TYPE_ID':'lists'
            }
    region = await b.get_all('lists.element.get',listsdata)
    numregdf = pd.DataFrame(region)
    for index,row in numregdf.iterrows():
        if pd.notna(row[REGUF]):
            try:
                if len(row[REGUF]) != 1:               
                    for i in row[REGUF].values():
                        regdict.update({i : row['ID']})
                else:
                    regdict.update({str(*row[REGUF].values()) : row['ID']})
            except:
                print(f'Не получилось подставить {row[REGUF]}')#, end="\r"
    del numregdf
    print('done count of list', len(regdict))

getlistregions()

def addleadcomment(id,region):
    comm_data={'fields':{
    "ENTITY_ID": id,
    "ENTITY_TYPE": 'lead',
    "COMMENT": str(f'Нет в списке - {region}, не удалось подставить нужного значения'),
    "AUTHOR_ID": 32
    }}
    requests.post(str(f'{URLBITRIX}/crm.timeline.comment.add.json'), json=comm_data)

app = FastAPI()

@app.post("/regionrequest/crm")
def requset_crm(ID:int,
              PHONE: int,
              AUTH: str| None = None
              ):
    if AUTH != ENVAUTH:
        return "AUTH ERR"
    params ={'num':PHONE}
    print(f'запрашиваю {ID} из {PHONE}')
    region = json.loads(requests.get(URLSERVICE, params = params).text)
    time.sleep(0.5)
    try:
        print(f"установлен регион{region['region']}")
        print(f"в словаре это{regdict[region['region']]}")
    except KeyError:
        addleadcomment(ID,region['region'])
        return "REG ERR"

    lead_data = {'id':ID,'fields':{
            'UF_CRM_PHONE_REGION': regdict[region['region']]
        }}
    requests.post(str(f'{URLBITRIX}/crm.lead.update.json'), json=lead_data)
    return "Response [200]"


@app.post("/regionrequest/webhook")
def request_webhook(PHONE: int,
                ID:int | None = 0,
                AUTH: str| None = None
                ):

    if AUTH != ENVAUTH:
        return "AUTH ERR"
    params ={'num':PHONE}
    print(f'запрашиваю {ID} из {PHONE}')
    
    region = json.loads(requests.get(URLSERVICE, params = params).text)
    time.sleep(0.5)   
    return {"data": region}
