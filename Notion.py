import requests

from doc import Internal_Integration_Token
from doc import Base_URL
from doc import DataBase_ID


header = {'Authorization': Internal_Integration_Token,
          'Notion-Version': '2021-08-16'}
query = {"filter": {"property": "Rank", "select": {"equals": True}}}

response = requests.post(Base_URL + DataBase_ID + '/query', headers=header, data=query)
#print(response)
#print(response.json()['results'])

def decoder(x):
    return[i for i in x]

print(response.json()['results'][0]['properties']['Rank']['select']['name'])