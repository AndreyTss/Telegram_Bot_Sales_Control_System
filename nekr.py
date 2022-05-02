import json
import requests

from doc import full_link

def ChangeCassaStatus():


    headers = {"Authorization": "Bearer " + 'secret_kZMZoIdqO5zhl3T5BaeAYdFEwSXq1PngWy6jCV0cPiB',
                        'Notion-Version': '2021-08-16',
                        'Content-Type': 'application/json'}

    dataJSONformat = {"properties": {"Cashier Status": {"rich_text": [{"text": {"content": "Novokosino"}}]}}}


    data = json.dumps(dataJSONformat)

    res = requests.request("PATCH", full_link, headers=headers, data=data)

    if res.status_code != 200:
        print(res.status_code)
        print(res.text)


ChangeCassaStatus()