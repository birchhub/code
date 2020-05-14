#!/usr/bin/python3
import http.server
import socketserver
import os
import sqlite3
import json
from urllib.parse import urlparse

DBPATH="/home/leo/helper/netdiscover.sqlite3"

def open_db(path):
    conn=None
    try:
        conn=sqlite3.connect(path)
    except ValueError as e:
        print(e)

    return conn
        
def get_free_ips(ipRange):
    conn=open_db(DBPATH)
    ips=[]
    if (conn):
        cur=conn.cursor()
        cur.execute(f"select ip from 'range{ipRange}' where status=0 order by lastonline desc")

        rows=cur.fetchall()
        for row in rows:
            ips.append(row[0])

    return ips

def netdiscover_overview(ipRange):
    conn=open_db(DBPATH)
    result=[]
    if (conn):
        cur=conn.cursor()
        cur.execute(f"select ip,status,lastonline,mac from 'range{ipRange}' order by lastonline")

        rows=cur.fetchall()
        for row in rows:
            # ip - status - lastseen
            next_ip = {"ip":row[0], "status":row[1], "lastOnline":row[2], "mac":row[3]}
            result.append(next_ip)

    return json.dumps(result )


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        response=""
        print(self.path)
        try:
            query=urlparse(self.path).query
            query_components=dict(qc.split("=") for qc in query.split("&"))
            ipRange=query_components["range"]

            if self.path.startswith("/available"):
                for ip in get_free_ips(ipRange):
                    response += f"{ip}\n"
                response += "\n"
            elif self.path.startswith("/overview"):
                response = netdiscover_overview(ipRange)
            else:
                raise ValueError("Bad Request")
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response.encode())
            #return http.server.SimpleHTTPRequestHandler.do_GET(self)
        except ValueError as e:
            print(e)
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"bad request\n")



# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 3141
socketserver.TCPServer.allow_reuse_address = True
my_server = socketserver.TCPServer(("", PORT), handler_object)

# Star the server
my_server.serve_forever()
