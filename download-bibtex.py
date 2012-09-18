from pyquery import PyQuery as pq
import urllib2,urllib
import re
import json
import bibtex
import itertools
import couchdb.client

def get_pages_list():
  base_url="http://www.biomedcentral.com/content?page=%s&itemsPerPage=100&citation=true&summary=false&format=BIBTEX_WITH_ABSTRACT"
  firstpage=base_url%1
  s=pq(url=firstpage)
  number=s(".pager .left").html()
  number=int(re.search("of ([0-9]+)",number).group(1))
  return [base_url%n for n in range(number+1)]

class Page:
  """ A page object, initialized with a url """
  
  def __init__(self,url):
    self.url=url
 
  def do(self):
    self.fetch()
    self.parse()
    self.get_bibtex()
    self.parse_bibtex()

  def fetch(self):
    self.pq=pq(url=self.url)
    
  def parse(self):
    self.article_ids=self.get_article_ids()

  def get_article_ids(self):
    for i in self.pq("form input"):
      if i.name=="articleIdThisPage":
        return i.value

  def get_bibtex(self):
    """ return the bibtex of the file """
    url="http://www.biomedcentral.com/download/citation"
    parameters={'citation':'on', 
      'result-selection':'THIS_PAGE',
      'suplements': 'false',
      'citationType':'BIBTEX_WITH_ABSTRACT',
      'articleIdThisPage':self.article_ids
      }
    data=urllib.urlencode(parameters)
    self.bibtex=urllib2.urlopen(url,data)
  
  def parse_bibtex(self):
    parser=bibtex.BibTexParser(self.bibtex)
    self.bibjson=[i for i in parser.parse()[0]]
    # TODO: Handle empty entries
    return self.bibjson

if __name__=="__main__":
  pages=[Page(u) for u in get_pages_list()]
  db=couchdb.client.Database('biomedcentral')
  for page in pages:
    try:
      page.do()
      for e in page.bibjson:
        db.save(e)
      db.commit()  
    except urllib2.HTTPError:
      print "Error at : %s"%page.url
