from flask import Flask
from flask_restplus import Api, Resource

import sqlite3
import json

flask_app = Flask(__name__)
app = Api(app = flask_app)

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
        except ValueError as e:
            print(e)
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
                print(next_ip)
        except:
            return []

    return result

def addMacDomainMapping(mac, domain):
    # curl --data '{"mac":"52:54:00:c1:58:6b", "domain":"kurtsMasterDomain"}' localhost:3141
    print(f"mac: {mac} - domain: {domain}")
    return
    conn=open_db(DBPATH)
    if conn:
        c = conn.cursor()
        cmd=f'insert or replace into macDomainMap values ("{mac}", "{domain}")'
        print(cmd)
        c.execute(cmd)
        conn.commit()


helper = app.namespace('', description='blegh')

@helper.route("/available/<string:range>/<int:mask>")
class MainClass(Resource):
    def get(self, range, mask):
        cidr=range+"/"+str(mask)
        iplist = get_free_ips(cidr)
        return iplist

@helper.route("/overview/<string:range>/<int:mask>")
class MainClass(Resource):
    def get(self, range, mask):
        cidr=range+"/"+str(mask)
        response = netdiscover_overview(cidr)
        return response

@helper.route("/addmac/<string:domain>/<string:mac>")
class MainClass(Resource):
    def post(self, domain, mac):
        addMacDomainMapping(mac, domain)
