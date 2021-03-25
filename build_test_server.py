#!/usr/local/bin/python3
import time
from pprint import pprint
import multiprocessing
from http.server import HTTPServer, CGIHTTPRequestHandler
import http.server
import socketserver
import json
import os
import sys
import util

# Used for SSEHandler:
import copy
import select
import urllib.parse
from http import HTTPStatus

nobody = None
SERVER_STATE_FILE = 'server_state.json'

# TODO: This file doesn't know about the new clients.json file
#       Which is where all the clients should be added to.
#       Rather refactor to not have to override existing client files
# FIXME: Why are all the bots being duplicated?

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
    genghis_client_dir = "" if len(sys.argv) != 3 else sys.argv[1]
    default = '~/genghis_client'
    while not genghis_client_dir:
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
    
    repetitions = "" if len(sys.argv) != 3 else sys.argv[2]
    default = "5"
    while not repetitions:
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

    process_client.start()
    process_game.start()

    with open('clients.json', 'r') as clients_file:
        clients_dict = json.load(clients_file)
    # Now build up a server_state.json file
    with open(SERVER_STATE_FILE, 'r') as server_state_file:
        server_state = json.load(server_state_file)
    server_state['endpoint'] = 'http://localhost:' + str(GAME_PORT) + "/"
    with open(os.path.join(genghis_client_dir, 'config.json'), 'r') as client_config:
        c_config = json.load(client_config)

    clients_dict['clients'] = []
    server_state['clients'] = []
    server_state['games'] = []
    for i in range(int(repetitions)):
        clients_dict['clients'].append({
            "username": c_config['username'] + "_" + str(i),
            "abbreviations": c_config.get('abbreviations', list(c_config['username'])),
            "url": 'http://localhost:' + str(CLIENT_PORT) 
        })
        # server_state['clients'].append({
        #     "username": c_config['username'] + "_" + str(i),
        #     "abbreviations": c_config.get('abbreviations', list(c_config['username'])),
        #     "url": 'http://localhost:' + str(CLIENT_PORT) 
        # })
    
    print(clients_dict.get('clients', []))
    with open('clients.json', 'w+') as clients_file:
        json.dump(clients_dict, clients_file, indent=2)

    with open(SERVER_STATE_FILE, 'w+') as server_state_file:
        json.dump(server_state, server_state_file, indent=2)

    time.sleep(1)
    print('''

===============================================================================

                                              ,,          ,,          
  .g8"""bgd                                 `7MM          db          
.dP'     `M                                   MM                      
dM'       `   .gP"Ya  `7MMpMMMb.   .P"Ybmmm   MMpMMMb.  `7MM  ,pP"Ybd 
MM           ,M'   Yb   MM    MM  :MI  I8     MM    MM    MM  8I   `" 
MM.    `7MMF'8M""""""   MM    MM   WmmmP"     MM    MM    MM  `YMMMa. 
`Mb.     MM  YM.    ,   MM    MM  8M          MM    MM    MM  L.   I8 
  `"bmmmdPY   `Mbmmd' .JMML  JMML. YMMMMMb  .JMML  JMML..JMML.M9mmmP' 
                                  6'     dP                           
   Genghis Bot Battle System      Ybmmmd'                             
   View the main game at https://people.cs.uct.ac.za/~KNXBOY001/genghis_server/
   You can also run this with commandline arguments: `python3 build_test_server {} {}`

===============================================================================
To view your game:
    1. Load up http://localhost:{} in Chrome (Other browsers may not work).
    2. Come back to this screen and press <ENTER>.
    3. Go back to Chrome and reload the page.
    4. Click on the first red link that appears once the page has loaded.

    '''.format(genghis_client_dir, repetitions, GAME_PORT))
    input("When you're ready, press any key to begin.\n".format(GAME_PORT))

    import build_game
    build_game.main(SERVER_STATE_FILE)
    print("Game has finished")

    process_client.join()
   #  print("Client Server has finished")
    process_game.join()
   #  print("Game Server has finished")

def start_server(directory='', PORT=8000):
    old_dir = os.path.dirname(__file__)
    if not directory:
        directory = os.path.dirname(__file__)

    os.chdir(directory)
    # Utilities for CGIHTTPRequestHandler
    def executable(path):
        """Test for executable file."""
        return os.access(path, os.X_OK)

    class SSEHandler(http.server.SimpleHTTPRequestHandler):
        # Determine platform specifics
        have_fork = hasattr(os, 'fork')

        # Make rfile unbuffered -- we need to read one line and then pass
        # the rest to a subprocess, so we can't use buffered input.
        rbufsize = 0

        def do_POST(self):
            """Serve a POST request.
            This is only implemented for CGI scripts.
            """

            if self.is_cgi():
                self.run_cgi()
            else:
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Can only POST to CGI scripts")

        def send_head(self):
            """Version of send_head that support CGI scripts"""
            if self.is_cgi():
                return self.run_cgi()
            else:
                return http.server.SimpleHTTPRequestHandler.send_head(self)

        def is_cgi(self):
            """Test whether self.path corresponds to a CGI script.
            Returns True and updates the cgi_info attribute to the tuple
            (dir, rest) if self.path requires running a CGI script.
            Returns False otherwise.
            If any exception is raised, the caller should assume that
            self.path was rejected as invalid and act accordingly.
            The default implementation tests whether the normalized url
            path begins with one of the strings in self.cgi_directories
            (and the next character is a '/' or the end of the string).
            """
            # Query component should not be involved.
            path, _, query = self.path.partition('?')
            path = urllib.parse.unquote(path)

            # Similar to os.path.split(os.path.normpath(path)) but specific to URL
            # path semantics rather than local operating system semantics.
            path_parts = path.split('/')
            head_parts = []
            for part in path_parts[:-1]:
                if part == '..':
                    head_parts.pop() # IndexError if more '..' than prior parts
                elif part and part != '.':
                    head_parts.append( part )
            if path_parts:
                tail_part = path_parts.pop()
                if tail_part:
                    if tail_part == '..':
                        head_parts.pop()
                        tail_part = ''
                    elif tail_part == '.':
                        tail_part = ''
            else:
                tail_part = ''

            if query:
                tail_part = '?'.join((tail_part, query))

            splitpath = ('/' + '/'.join(head_parts), tail_part)
            collapsed_path = "/".join(splitpath)
            dir_sep = collapsed_path.find('/', 1)
            while dir_sep > 0 and not collapsed_path[:dir_sep] in self.cgi_directories:
                dir_sep = collapsed_path.find('/', dir_sep+1)
            if dir_sep > 0:
                head, tail = collapsed_path[:dir_sep], collapsed_path[dir_sep+1:]
                self.cgi_info = head, tail
                return True
            return False

        # TODO: try to have a specific script be the cgi 'directory'
        cgi_directories = ['/cgi-bin', '/htbin']

        def is_executable(self, path):
            """Test whether argument path is an executable file."""
            return os.access(path, os.X_OK)

        def is_python(self, path):
            """Test whether argument path is a Python script."""
            head, tail = os.path.splitext(path)
            return tail.lower() in (".py", ".pyw")

        def run_cgi(self):
            """Execute a CGI script."""
            print("doing cgi")
            dir, rest = self.cgi_info
            path = dir + '/' + rest
            i = path.find('/', len(dir)+1)
            while i >= 0:
                nextdir = path[:i]
                nextrest = path[i+1:]

                scriptdir = self.translate_path(nextdir)
                if os.path.isdir(scriptdir):
                    dir, rest = nextdir, nextrest
                    i = path.find('/', len(dir)+1)
                else:
                    break

            # find an explicit query string, if present.
            rest, _, query = rest.partition('?')

            # dissect the part after the directory name into a script name &
            # a possible additional path, to be stored in PATH_INFO.
            i = rest.find('/')
            if i >= 0:
                script, rest = rest[:i], rest[i:]
            else:
                script, rest = rest, ''

            scriptname = dir + '/' + script
            scriptfile = self.translate_path(scriptname)
            if not os.path.exists(scriptfile):
                self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "No such CGI script (%r)" % scriptname)
                return
            if not os.path.isfile(scriptfile):
                self.send_error(
                    HTTPStatus.FORBIDDEN,
                    "CGI script is not a plain file (%r)" % scriptname)
                return
            ispy = self.is_python(scriptname)
            if self.have_fork or not ispy:
                if not self.is_executable(scriptfile):
                    self.send_error(
                        HTTPStatus.FORBIDDEN,
                        "CGI script is not executable (%r)" % scriptname)
                    return

#            # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
#            # XXX Much of the following could be prepared ahead of time!
            env = copy.deepcopy(os.environ)
            env['SERVER_SOFTWARE'] = self.version_string()
            env['SERVER_NAME'] = self.server.server_name
            env['GATEWAY_INTERFACE'] = 'CGI/1.1'
            env['SERVER_PROTOCOL'] = self.protocol_version
            env['SERVER_PORT'] = str(self.server.server_port)
            env['REQUEST_METHOD'] = self.command
            uqrest = urllib.parse.unquote(rest)
            env['PATH_INFO'] = uqrest
            env['PATH_TRANSLATED'] = self.translate_path(uqrest)
            env['SCRIPT_NAME'] = scriptname
            if query:
                env['QUERY_STRING'] = query
            env['REMOTE_ADDR'] = self.client_address[0]
            authorization = self.headers.get("authorization")
            if authorization:
                authorization = authorization.split()
                if len(authorization) == 2:
                    import base64, binascii
                    env['AUTH_TYPE'] = authorization[0]
                    if authorization[0].lower() == "basic":
                        try:
                            authorization = authorization[1].encode('ascii')
                            authorization = base64.decodebytes(authorization).\
                                            decode('ascii')
                        except (binascii.Error, UnicodeError):
                            pass
                        else:
                            authorization = authorization.split(':')
                            if len(authorization) == 2:
                                env['REMOTE_USER'] = authorization[0]
            # XXX REMOTE_IDENT
            if self.headers.get('content-type') is None:
                env['CONTENT_TYPE'] = self.headers.get_content_type()
            else:
                env['CONTENT_TYPE'] = self.headers['content-type']


            length = self.headers.get('content-length')
            if length:
                env['CONTENT_LENGTH'] = length
            referer = self.headers.get('referer')
            if referer:
                env['HTTP_REFERER'] = referer
            accept = self.headers.get_all('accept', ())
            env['HTTP_ACCEPT'] = ','.join(accept)
            ua = self.headers.get('user-agent')
            if ua:
                env['HTTP_USER_AGENT'] = ua
            co = filter(None, self.headers.get_all('cookie', []))
            cookie_str = ', '.join(co)
            if cookie_str:
                env['HTTP_COOKIE'] = cookie_str
            # XXX Other HTTP_* headers
            # Since we're setting the env in the parent, provide empty
            # values to override previously set values
            for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH',
                    'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER'):
                env.setdefault(k, "")

            self.send_response(HTTPStatus.OK, "OK")
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Content-Type', 'text/event-stream;charset=UTF-8')
            self.send_header('Keep-Alive', 'timeout=5, max=94')
            self.send_header('Connection', 'Keep-Alive')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()

            decoded_query = query.replace('+', ' ')

            if self.have_fork:
                # Unix -- fork as we should
                args = [script]
                if '=' not in decoded_query:
                    args.append(decoded_query)
                """Internal routine to get nobody's uid"""
                global nobody
                if not nobody:
                    try:
                        import pwd
                    except ImportError:
                        nobody = -1
                    try:
                        nobody = pwd.getpwnam('nobody')[2]
                    except KeyError:
                        nobody = 1 + max(x[2] for x in pwd.getpwall())
                self.wfile.flush() # Always flush before forking
                pid = os.fork()
                if pid != 0:
                    # Parent
                    pid, sts = os.waitpid(pid, 0)
                    # throw away additional data [see bug #427345]
                    while select.select([self.rfile], [], [], 0)[0]:
                        if not self.rfile.read(1):
                            break
                    exitcode = os.waitstatus_to_exitcode(sts)
                    if exitcode:
                        self.log_error(f"CGI script exit code {exitcode}")
                    return
                # Child
                try:
                    try:
                        os.setuid(nobody)
                    except OSError:
                        pass
                    os.dup2(self.rfile.fileno(), 0)
                    os.dup2(self.wfile.fileno(), 1)
                    os.execve(scriptfile, args, env)
                except:
                    self.server.handle_error(self.request, self.client_address)
                    os._exit(127)

            else:
                # Non-Unix -- use subprocess
                import subprocess
                cmdline = [scriptfile]
                if self.is_python(scriptfile):
                    interp = sys.executable
                    if interp.lower().endswith("w.exe"):
                        # On Windows, use python.exe, not pythonw.exe
                        interp = interp[:-5] + interp[-4:]
                    cmdline = [interp, '-u'] + cmdline
                if '=' not in query:
                    cmdline.append(query)
                self.log_message("command: %s", subprocess.list2cmdline(cmdline))
                try:
                    nbytes = int(length)
                except (TypeError, ValueError):
                    nbytes = 0
                p = subprocess.Popen(cmdline,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    env = env
                                    )
                if self.command.lower() == "post" and nbytes > 0:
                    data = self.rfile.read(nbytes)
                else:
                    data = None
                # throw away additional data [see bug #427345]
                while select.select([self.rfile._sock], [], [], 0)[0]:
                    if not self.rfile._sock.recv(1):
                        break
                stdout, stderr = p.communicate(data)
                self.wfile.write(stdout)
                if stderr:
                    self.log_error('%s', stderr)
                p.stderr.close()
                p.stdout.close()
                status = p.returncode
                if status:
                    self.log_error("CGI script exit status %#x", status)
                else:
                    self.log_message("CGI script exited OK")


    attempts = 0
    while True:
        assert attempts < 500
        try:
            httpd = HTTPServer(("", PORT + attempts), SSEHandler)
            break
        except OSError:
            attempts += 1

    print("Server created at http://localhost:{}/ on directory {}".format(PORT, directory))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server closed at http://localhost:{}/ on directory {}".format(PORT, directory))
    os.chdir(old_dir)

    
if __name__ == '__main__':
    try:
        main()
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


