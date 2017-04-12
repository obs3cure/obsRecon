import argparse
import json
import requests
import codecs
import locale
import os
import sys
import ast

   
class Censys:
     
    def __init__(self, ip,certf ):
 
        self.API_URL = "https://www.censys.io/api/v1"
        self.UID = "tu uid"
        self.SECRET = "tu secret"
        self.ip = ip
        self.cert = certf
        self.names = []
        self.namesProcesed = []
 
    

    def search4certs(self):
 
        pages = float('inf')
        page = 1
 
        while page <= pages:  
 
            params = {'query' : self.cert, 'page' : page, 'fields' : ["ip", "443.https.tls.certificate.parsed.names", "protocols"]  }
            res = requests.post(self.API_URL + "/search/ipv4", json = params, auth = (self.UID, self.SECRET))
            payload = res.json()
           
 
            for r in payload['results']:
               
                ip = r["ip"]
                self.ip=ip
                #self.search()
                proto = r["protocols"]
                proto = [p.split("/")[0] for p in proto]
                proto.sort(key=float)
                protoList = ','.join(map(str, proto))

                ns = r["443.https.tls.certificate.parsed.names"]
                ns = [p.split("/")[0] for p in ns]
                nsList = ','.join(map(str, ns)) 
                print r["ip"], nsList, proto

                #[x.strip() for x in nsList.split(',')]
                for t in ns:
                    #while (t.count('.')>1):
                       #t=t.split('.', 1)[1]
                     if t not in self.names and t not in self.namesProcesed:
                         self.names.append(t)
                         
             
            
            
 
            pages = payload['metadata']['pages']
            page += 1
 

ip="1.1.1.1"
certf = "443.https.tls.certificate.parsed.names: *quiron* and location.country_code: ES"
censys = Censys(ip,certf)
censys.search4certs()
