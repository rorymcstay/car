import json

import requests

body = {
    "result_css": ".card__body",
    "result_exclude": "Compare, compare, insurance, Insurance",
    "wait_for_car": ".cad-header",
    "json_identifier": "window.adDetails",
    "next_page_xpath": "/html/body/main/div[1]/div/div[2]/paging/nav/button[12]/span",
    "sort": "publishdate%20desc"
}

header = {
    "Content-Type": "application/json"
}

r = requests.put(url='http://127.0.0.1:5000/containermanager/add_market/donedeal',
                 json=json.dumps(body),
                 headers=header)


print r.status_code
print r.content