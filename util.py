import json
import requests


class Client:
    def __init__(self, username, url, abbreviations):
        self.username = username
        self.url = url
        self.abbreviations = abbreviations[:]
        r = requests.get(self.root_url + "/config.json")
        if r.ok:
            self.bots = []
            for item in r.json()['bots']:
                path = self.root_url + '/' + item['path']
                if requests.get(path).ok:
                    self.bots.append(self.root_url + '/' + item['path'])
                else:
                    print(r.text)

            self.battlegrounds = []
            for item in r.json()['battlegrounds']:
                path = self.root_url + '/' + item['path']
                if requests.get(path).ok:
                    self.battlegrounds.append(self.root_url + '/' + item['path'])
                else:
                    print(r.text)
        else:
            print(r.text)
            print(r.status_code)


class Bot:
    def __init__(self, script_url):
        self.script_url = script_url
