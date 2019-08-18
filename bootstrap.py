#!/usr/bin/env python
import sys
print(sys.version_info)
#######################################
# from python 3 HTTPServer has been move to http.server
# the following code is import library from different version
# of python.
# determine the python version code
if sys.version_info[0] > 2:
    from http.server import *
else:
    from BaseHTTPServer import *
    
#######################################
import os
import re
import subprocess
import shlex

VIDEO_PATH='video'
PLAIN_TEXT_FILE_SUFFIX_LIST=('.js','.py','.cast','.html','.css')

class ASCII_Player(BaseHTTPRequestHandler):
    
    def do_GET(self):
        m = re.match(r'(?P<filepath>/' + VIDEO_PATH + '/.*)\?play',self.path)
        if m:
            self.send_response(200)
            self.end_headers()
            play_file = m.groupdict()['filepath']
            if sys.version_info[0] > 2:
                self.wfile.write( self.format_player(play_file).encode())
            else:
                self.wfile.write( self.format_player(play_file))
            return

        n = re.match(r'/$', self.path)
        if n:
            filelist = self.search()
            response = 'NO {0} sub-folder in current directory'.format(VIDEO_PATH)
            if filelist:
                response = '<html><body><div>'
                self.send_response(200)
                for f in filelist:
                    response += '<a href="{0}/{1}?play">{1}</a><br>'.format(VIDEO_PATH,f)
                    response += '</div></body></html>'
                else:
                    self.send_response(404)
            self.end_headers()
            if sys.version_info[0] > 2:
                self.wfile.write(response.encode('UTF-8'))
            else:
                self.wfile.write(response)
            return
        j = re.match(r'/(?P<filepath>.*\..*)$', self.path)
        if j:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), j.groupdict()['filepath'])
            is_plain = self.is_plain_text_file(path)
            if os.path.exists(path):
                # Only linux support, by call "file --mine-type <filename>"
                
                if self.is_plain_text_file(path):
                    f = open(path,encoding='UTF-8')
                else:
                    f= open(path,'rb')
                
                response = f.read()
                try:
                    self.end_headers()
                except:
                    pass
                if sys.version_info[0] > 2:
                    self.wfile.write(response.encode('UTF-8') if is_plain else response )
                else:
                    self.wfile.write(response)
                f.close()
            else:
                self.send_response(404)

    def is_plain_text_file(self, path):
        #cmd = shlex.split('file --mine-type {0}'.format(path))
        #result = subprocess.check_output(cmd)
        #mine_type = result.split()[-1]
        for suffix in PLAIN_TEXT_FILE_SUFFIX_LIST:
            if path.endswith(suffix):
                return True
        return False
        
    def search(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),VIDEO_PATH)
        if os.path.exists(path):
            filelist = os.listdir(path)
            castlist = filter(lambda f: f.endswith('.cast'), filelist)
            return castlist
        return None
    
    def format_player(self, path):
        with open('template.html') as tpl:
            content = tpl.read()
            return re.sub(r'@@VIDEO@@', path, content)


print("Open browser and type \"http://localhost:8080/\"")
server_address = ('', 8080)
httpd = HTTPServer(server_address,ASCII_Player)
httpd.serve_forever()
