import json

import requests

class Client:
    def __init__(self, url):
        self.url = url

    def projection_request(self, body= None):
        header = {
            "Content-Type": "application/json"
        }

        r = requests.put(url=self.url,
                         json=json.dumps(body),
                         headers=header)
        return json.loads(r.text)
