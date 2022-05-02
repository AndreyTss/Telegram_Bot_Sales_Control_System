import json
import requests

from doc import full_link
from doc import Internal_Integration_Token

def ChangeCassaStatus():

    headers = {"Authorization": "Bearer " + Internal_Integration_Token,
                        'Notion-Version': '2021-08-16',
                        'Content-Type': 'application/json'}

    dataJSONformat = {"properties": {"Cashier Status": {"rich_text": [{"text": {"content": "Novokosino"}}]}}}


    data = json.dumps(dataJSONformat)

    res = requests.request("PATCH", full_link, headers=headers, data=data)

    if res.status_code != 200:
        print(res.status_code)
        print(res.text)


ChangeCassaStatus()