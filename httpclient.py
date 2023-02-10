#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately

import urllib.parse

PORT=80
User_Agent=""

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        #parse the url first
        parse_url=urllib.parse.urlsplit(url)
        try:
            if ":" in parse_url.netloc:
                #Host, port
                return parse_url.netloc.split(":")[0], int(parse_url.netloc.split(":")[1])
            else:
                return socket.gethostbyname(parse_url.netloc),80
        except:
            return None, None


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        print("data:")
        #If there is nothing, return nothing
        if not data:
            return None
        
        data_lines=data.splitlines()
        #again, testing if there are data
        if data_lines=="" or data_lines==None:
            return None
        # print("data lines?")
        # print(data_lines)
        #It goes HTTP/1.0 code ok(?), Server:...
        try:
            code=int(data_lines[0].split()[1])
        except:
            return None
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        #Split the data
        data_lines=data.split('\r\n\r\n')
        body=""
        #To see the datas
        print("Split data: ")
        print(data_lines)
        if len(data_lines)>=2:
            #For post data mostly, put the body/args at the back
            for line in data_lines[1:]:
                print("lines: "+line)
                body+=line
        print("Body is "+body)
        return body
        # data_lines=data.splitlines()
        # try:
        #     index=0
        #     for line in data_lines:
        #         index+=1
        #         if len(line)==0:
        #             return data_lines.splitlines()[index]
        # except:
        #     return ""
        # return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        print("a")
        done = False
        while not done:

            part = sock.recv(1024)
            print("c")
            if (part):
                buffer.extend(part)
                #socket.socket.shutdown(socket.SHUT_WR)
            else:
                done = not part
        
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        host,port=self.get_host_port(url)
        
        parsed_url=urllib.parse.urlparse(url)
        scheme=parsed_url.scheme
        path=parsed_url.path
        #Only accept http, make sure the path is there,make sure there is a valid host, use 80 as port as default
        if scheme!="http":
            print("Not http")
            return None
        if len(path)==0:
            path="/"
        if host==None:
            return HTTPResponse(404,None)
        if port==None:
            port=80
        print(parsed_url)
        self.connect(host,port)
        #change from simply concatenating host to formatting parsed_url.netloc
        headers="HTTP/1.1\r\nHost: {}".format(parsed_url.netloc)+"\r\n"
        headers+="User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0\r\n"
        headers+="Connection: close\r\n\r\n"
        request = "GET {} {}\r\n".format(path, headers)
        self.sendall(request)
        response=self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)
        #print("Here is code"+code)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host,port=self.get_host_port(url)
        
        parsed_url=urllib.parse.urlparse(url)
        scheme=parsed_url.scheme
        path=parsed_url.path
        #Same thing as GET
        if scheme!="http":
            print("Not http")
            return None
        if len(path)==0:
            path="/"
        if host==None:
            return HTTPResponse(404,None)
        if port==None:
            port=80
        
        
        self.connect(host,port)
        print("Try args")
        arguments=""
        if args != None:
            print(args)
            #Parse the arguments
            arguments = urllib.parse.urlencode(args)
            print("Print arguments")
            print(arguments)
            print(len(arguments))    
        print("It passed")
        headers="HTTP/1.1\r\nHost: "+host+"\r\nAccept-Charset: UTF-8\r\n"
        headers+="Content-Type: application/x-www-form-urlencoded\r\n"
        headers+="Content-Length: {}\r\n".format(len(arguments))
        print("Pass again")
        headers+="User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0\r\n"
        headers+="Connection: close\r\n\r\n{}\r\n\r\n".format(arguments)
        request = "POST {} {}\r\n".format(path, headers)
        print("Request: "+request)
        print("End here")
        self.sendall(request)
        print("End here")
        #This is inspired by the post https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2196981
        #Method taken from Fahad Naveed
        #Without shutdown, it will stuck
        self.socket.shutdown(socket.SHUT_WR)
        response=self.recvall(self.socket)
        
       

        self.close()
        code = self.get_code(response)
        body = self.get_body(response)
        # print("Here is code"+code)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
