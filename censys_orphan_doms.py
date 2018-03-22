import requests
import sys
import pygeoip
import whois


class Censys:
    def __init__(self, ip, certf):

        self.API_URL = "https://www.censys.io/api/v1"
        self.UID = "your id"
        self.SECRET = "yoursecret"
        self.ip = ip
        self.cert = certf
        self.names = []
        self.namesProcesed = []
        self.GEOIP = pygeoip.GeoIP("GeoIP.dat", pygeoip.MEMORY_CACHE)
        self.available = []


    def search4certs(self):

        pages = float('inf')
        page = 1

        while page <= pages:

            params = {'query': self.cert, 'page': page,
                      'fields': ["ip", "443.https.tls.certificate.parsed.names", "protocols"]}
            res = requests.post(self.API_URL + "/search/ipv4", json=params, auth=(self.UID, self.SECRET))
            if res.status_code != 200:
                print "error occurred: %s" % res.json()["error"]
                sys.exit(1)
            payload = res.json()

            for r in payload['results']:

                ip = r["ip"]
                self.ip = ip
                # self.search()
                proto = r["protocols"]
                proto = [p.split("/")[0] for p in proto]
                proto.sort(key=float)
                protoList = ','.join(map(str, proto))

                ns = r["443.https.tls.certificate.parsed.names"]
                ns = [p.split("/")[0] for p in ns]
                #La parte de busqueda de dominios sin registrar
                for dom in ns:
                    try:
                        dom = dom.replace("*.", "")#quito wildcards

                        if dom is not None and dom != '':
                            details = whois.query(str(dom))
                            if details.creation_date is not None:
                                pass
                            else:
                                self.available.append(dom)
                    except Exception:
                        pass
                        #all known TLD: ['co', 'it', 'cz', 'at', 'eu', 'ru', 'lv', 'nz', 'net', 'pl', 'be', 'fr', 'de', 'jp', 'me', 'co_jp', 'biz', 'org', 'info', 'name', 'us', 'uk', 'com'])
                nsList = ','.join(map(str, ns))
                country = self.GEOIP.country_name_by_addr(ip)

                print r["ip"], country,nsList, proto

                # [x.strip() for x in nsList.split(',')]
                for t in ns:
                    # while (t.count('.')>1):
                    # t=t.split('.', 1)[1]
                    if t not in self.names and t not in self.namesProcesed:
                        self.names.append(t)

            pages = payload['metadata']['pages']
            page += 1

    def printAvailability(self):

        print "-----------------------------"
        print "Available Domains: "
        print "-----------------------------"
        for av in self.available:
            print av


ip = "1.1.1.1"
certf = "443.https.tls.certificate.parsed.names: apple*"
censys = Censys(ip, certf)
censys.search4certs()
censys.printAvailability()
