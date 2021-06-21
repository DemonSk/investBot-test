import requests
import json

def getfear():
    url = "https://api.alternative.me/fng/?limit=2"
    response = requests.request("GET", url)
    res = response.text
    res_dict = json.loads(res)
    return res_dict['data'][0]['value']
