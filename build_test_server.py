#!/usr/local/bin/python3
import time
import multiprocessing
import http.server
import socketserver
import json
import os
import sys
import util

SERVER_STATE_FILE = 'server_state.json' if len(sys.argv) < 2 else sys.argv[1]

def main():
    """
    This is the script to build a localhost test server, for testing bots
    on the Genghis Bot Battle System.

    If this script is called without parameters, an interactive prompt 
    will guide the user in setting up the test server, and eventually
    write all the parameters out to the server_state.json file which 
    stores the configurations for the server.

    To use a pre-existing server_state.json file, call this script with
    only that file's name as a parameter:
    ```
    ./build_test_server.py my_server_state_file.json
    ```
    """
    print("At any time, enter a question mark (?) and then press <ENTER> for help.")
    genghis_client_dir = ""
    while not genghis_client_dir:
        default = '~/genghis_client'
        genghis_client_dir = input("genghis_client directory ['{}']: ".format(default)).strip()
        if genghis_client_dir == "?":
            print("genghis_client Directory Explanation\n" +
            "The genghis_client directory is the absolute path to your local 'genghis_client' directory\n" + 
            "in which your bot script, your 'config.json' file, and your battleground\n" +
            "file are all found.\n" + 
            "This is probably just '~/genghis_client'.")
            genghis_client_dir = ""
            continue
        elif genghis_client_dir == "":
            genghis_client_dir = default
        if False:
            pass
            # TODO Do some checking for the bot path
    genghis_client_dir = os.path.expanduser(genghis_client_dir)
    
    repetitions = "" 
    while not repetitions:
        default = "3"
        repetitions = input("Number of Repetitions ['{}']: ".format(default)).strip()
        if repetitions == "?":
            print("Repetitions Explanation:\n" + 
                "The number of repetitions is how many copies of the bots found\n" + 
                "in the `genghis_client` directory you want to be included in the\n" + 
                "game to be built.\n" + 
                "If you want to use bots from multiple directories, or want to \n" + 
                "choose exactly which battleground / bot combinations you want, \n" + 
                "you'll need to make your own `server_state.json` file and pass\n" + 
                "it in as an argument to this script.")
            repetitions = ""
            continue
        elif repetitions == "":
            repetitions = default
        if False:
            pass
            # TODO Do some checking for the bot path

    # Start up a server for the genghis_client
    # Start up a server for the game
    # TODO maybe this should rather be in one of the game methods, and called when build_game sees that endpoint is localhost?
    GAME_PORT = 5000
    process_game = multiprocessing.Process(target=start_server, kwargs={'directory':os.path.dirname(os.path.abspath(__file__)), 'PORT': GAME_PORT})

    CLIENT_PORT = 4000
    process_client = multiprocessing.Process(target=start_server, kwargs={'directory':genghis_client_dir, 'PORT':CLIENT_PORT})

    process_game.start()
    process_client.start()

    # Now build up a server_state.json file
    with open(SERVER_STATE_FILE, 'r') as server_state_file:
        server_state = json.load(server_state_file)
    server_state['endpoint'] = 'localhost:' + str(GAME_PORT) + "/"
    with open(os.path.join(genghis_client_dir, 'config.json'), 'r') as client_config:
        c_config = json.load(client_config)

    server_state['clients'] = []
    server_state['games'] = []
    for i in range(int(repetitions)):
        server_state['clients'].append({
            "username": c_config['username'] + "_" + str(i),
            "abbreviations": c_config['abbreviations'],
            "url": 'http://localhost:' + str(CLIENT_PORT) 
        })
    
    with open(SERVER_STATE_FILE, 'w+') as server_state_file:
        json.dump(server_state, server_state_file, indent=2)

    time.sleep(1)
    import build_game
    build_game.main(SERVER_STATE_FILE)

    process_client.join()
    process_game.join()

def start_server(directory='', PORT=8000):
    old_dir = os.path.dirname(__file__)
    if not directory:
        directory = os.path.dirname(__file__)

    os.chdir(directory)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("localhost", PORT), Handler) as httpd:
        print("Serving at port {}, on directory {}".format(PORT, directory))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
    os.chdir(old_dir)

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)


