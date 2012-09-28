import urllib
import urllib2
import cookielib
import sys

baseurl="http://dump.tentacleriot.eu/bmc"

opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
urllib2.install_opener(opener)

def login(user,pw):
  data=urllib.urlencode({"username":user,"password":pw})
  f=urllib2.urlopen("http://bibsoup.net/account/login",data)
  return [i for i in f]

def upload(fl):
  url="http://bibsoup.net/upload"
  data=urllib.urlencode({"source":"%s/%s"%(baseurl,fl),
    "collection":"Biomedcentral",
    "description":"""References from Biomedcentral scraped at #OKFest2012 on
    September 19th""",
    "license":"http://www.opendefinition.org/licenses/cc-zero",
    "format":"json"
    })
  f=urllib2.urlopen(url,data)
  return [i for i in f]


    
script=sys.argv.pop(0)    
user=sys.argv.pop(0)
pw=sys.argv.pop(0)
print user
print pw
print login(user,pw)
for f in sys.argv:
  upload(f) 
