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
        try:
            cur=conn.cursor()
            cur.execute(f"select ip from 'range{ipRange}' where status=0 order by lastonline asc")

            rows=cur.fetchall()
            for row in rows:
                ips.append(row[0])
        except:
            return []

    return ips

def netdiscover_overview(ipRange):
    # wget -O - 127.0.0.1:2222/overview?range=10.17.76.0/24
    conn=open_db(DBPATH)
    result=[]
    if (conn):
        try:
            cur=conn.cursor()
            cur.execute(f"select ip,status,lastonline,range.mac,m1.domain,"
                        f"range.dup1,m2.domain,range.dup2,m3.domain "
                        f"from 'range{ipRange}' as range "
                        f"left join macDomainMap as m1 on range.mac = m1.mac " 
                        f"left join macDomainMap as m2 on (range.dup1 = m2.mac) "
                        f"left join macDomainMap as m3 on (range.dup2 = m3.mac)")

            rows=cur.fetchall()
            for row in rows:
                mac=row[3]
                domainname=row[4]
                if not domainname:
                    domainname = ""
                dup1=row[5]
                if dup1 and dup1 != "na":
                    mac += f" {dup1}"
                    domainname += f" {row[6]}"
                    dup2=row[7]
                    if dup2 and dup2 != "na":
                        mac += f" {dup2}"
                        domainname += f" {row[8]}"

                next_ip = {"ip":row[0], "status":row[1], "lastOnline":row[2], "mac":mac, "domainname":domainname}
                result.append(next_ip)
        except:
            return json.dumps([])

    return json.dumps(result)

def addMacDomainMapping(mac, domain):
    # curl --data '{"mac":"52:54:00:c1:58:6b", "domain":"kurtsMasterDomain"}' localhost:3141
    conn=open_db(DBPATH)
    if conn:
        c = conn.cursor()
        cmd=f'insert or replace into macDomainMap values ("{mac}", "{domain}")'
        print(cmd)
        c.execute(cmd)
        conn.commit()


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        #self._set_headers()
        print("in post method")
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()
        print(self.data_string)
        data = json.loads(self.data_string)
        
        mac=data["mac"]
        domain=data["domain"]
        addMacDomainMapping(mac, domain)

        return

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
