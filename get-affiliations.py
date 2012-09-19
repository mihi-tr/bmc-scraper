from pyquery import PyQuery as pq
import couchdb.client
import re
import urllib2

class Article:
  def __init__(self,url):
    self.url=url
    self.s=pq(url=self.url)
  
  def has_fulltext(self):
    html=self.s("div#viewing-options-links").html()
    return re.search("Full text",html)

  def parse_author_entry(self,entry):
    aname=re.compile("^([^<]+)")
    name=aname.search(entry).group(1)
    affiliation=re.compile(">([0-9]+)</a>")
    affiliations=[int(i) for i in affiliation.findall(entry)]
    return {"longname":name,"affiliations":affiliations}

  def get_authors(self):
    authors="%s"%self.s("p.authors")
    authors=authors.split("<strong>")[1:]
    authors=[self.parse_author_entry(e) for e in authors]
    affiliations=self.get_affiliations()
    for a in authors:
      a["affiliations"]=[affiliations[aff] for aff in a["affiliations"]]
    return authors    
 
  def get_affiliation_text(self,element):
    text=element.text_content().strip()[1:]
    return "".join(text).lstrip()

  def get_affiliations(self):
   affiliations=self.s("div#ins_container p")
   affiliations=dict([(int(a.find("sup").text),
   self.get_affiliation_text(a)) for a in
   affiliations])
   return affiliations


if __name__=="__main__":
  db=couchdb.client.Database('biomedcentral')
  lastid=None
  fn="""function(d) {if ((! d.author[0].affiliations) && (! d.error)) {
    emit(d.autor)}}"""
  try:
    design=db["_design/biomedcentral"]
    design["views"]["get_no_affiliates"]["map"]=fn
  except:
    design={"views": {"get_no_affiliates": {
    "map": fn
    }
    }
    }
  db["_design/biomedcentral"]=design  
  result=db.view("biomedcentral/get_no_affiliates", limit=100)
  while (result):
    for row in result:
      id=row.id
      entry=db[id]
      try:
        art=Article(entry["link"][0]["url"])
        authors=art.get_authors()
        for i in range(len(authors)):
          entry["author"][i]={u'name':entry["author"][i]["name"],
          u'id':entry["author"][i]["id"],
          "affiliations":authors[i]["affiliations"]}
        db[id]=entry  
        print id
      except:
        print "Error with url on %s"%id
        entry["error"]=1
        db[id]=entry
      lastid=id  
    result=db.view("biomedcentral/get_no_affiliates", limit=100,
    startkey_docid=lastid)
    


