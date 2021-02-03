#!/usr/bin/python3
from Crypto.PublicKey import RSA
import datetime
import json
import os
import requests
import shutil
import subprocess
import sys
import time
import traceback

def main():
    # Open up clients.json, for checking new against old
    with open('clients.json', 'r') as clients_file:
        clients_json = json.load(clients_file)
    clients = clients_json.get('clients', [])
    # Open up .new_clients.json, for processing the new
    with open('.new_clients.json', 'r') as new_clients_file:
        new_clients_json = json.load(new_clients_file)
    new_clients = new_clients_json.get('clients', [])

    new_clients_to_write = []
    print("{} new client(s) to process at {}".format(len(new_clients), datetime.datetime.now()))
    for client in new_clients:
        subdirectory = client.get('url').replace('https://github.com/', '')
        dirname = "/home/k/knxboy001/.ssh/genghis/{}/".format(subdirectory)
        if not client.get('public_key'):
            print("Client at {} doesn't have a public key, generating...".format(client.get('url')))
            # Generate a public key
            key = RSA.generate(2048)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
                os.chmod(dirname, 0o700)
            with open(dirname + "id_rsa", 'wb') as content_file:
                os.chmod(dirname + "id_rsa", 0o600)
                content_file.write(key.exportKey('PEM'))

            pubkey = key.publickey()
            with open(dirname + 'id_rsa.pub', 'wb') as content_file:
                content_file.write(pubkey.exportKey('OpenSSH'))

            client['public_key'] = pubkey.exportKey('OpenSSH').decode('utf-8')
            new_clients_to_write.append(client)
        else:
            print("Client at {} does have a public key, checking github...".format(client.get('url')))
            cmd = ['ssh-agent', 'bash', '-c', 'ssh-add {} && git clone git@github.com:{}/{}.git'.format(dirname + 'id_rsa', client.get('username'), client.get('repository'))]
            print(' '.join(cmd))
            proc = subprocess.run(cmd)
            if proc.returncode != 0:
                if not client.get('first_failure'):
                    client['first_failure'] = str(datetime.datetime.now())
                    new_clients_to_write.append(client)
                elif datetime.datetime.now() - datetime.datetime.strptime(client['first_failure'], '%Y-%m-%d %H:%M:%S.%f') < datetime.timedelta(seconds=300):
                    new_clients_to_write.append(client)
                print('Cmd FAILED with error {}'.format(proc.returncode))
                print(proc.stdout)
                print(proc.stderr)
                continue
            print('Success with client at {}, adding to clients.json'.format(client.get('url')))
            client.pop('case', None)
            client['abbreviations'] = list(client['username'])
            clients.append(client)
            subprocess.run([ "rm", "-rf","{}".format(client.get('repository'))])

    # Finally, clear the .new_clients.json file to show that all has been processed
    clients_json['clients'] = clients
    with open('clients.json', 'w+') as clients_file:
        json.dump(clients_json, clients_file, indent=2)

    new_clients_json['clients'] = new_clients_to_write
    with open('.new_clients.json', 'w+') as new_clients_file:
        json.dump(new_clients_json, new_clients_file, indent=2)

if __name__ == '__main__':
    for _ in range(10):
        main()
        time.sleep(5)


