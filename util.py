import json
import requests


class Client:
    def __init__(self, username, url, abbreviations):
        self.username = username
        self.url = url
        self.abbreviations = abbreviations[:]
        r = requests.get(self.url + "/config.json")
        assert r.ok, self.url + "/config.json\n" + r.text
        self.bots = []
        json_result = r.json() 
        for item in json_result['bots']:
            path = self.url + '/' + item['path']
            r = requests.get(path)
            assert r.ok, path + r.text
            self.bots.append(self.url + '/' + item['path'])

        self.battlegrounds = []
        for item in json_result['battlegrounds']:
            path = self.url + '/' + item['path']
            r = requests.get(path)
            assert r.ok, path + r.text
            self.battlegrounds.append(self.url + '/' + item['path'])


class Bot:
    def __init__(self, script_url):
        self.script_url = script_url
