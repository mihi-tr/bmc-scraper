from pyquery import PyQuery as pq
import re

class Article:
  def __init__(self,url):
    self.url=url
    self.s=pq(url=self.url)
  
  def has_fulltext(self):
    html=self.s("div#viewing-options-links").html()
    print html
    return re.search("Full text",html)

  def parse_author_entry(self,entry):
    aname=re.compile("^([^<]+)")
    name=aname.search(entry).group(1)
    affiliation=re.compile(">([0-9]+)</a>")
    affiliations=[int(i) for i in affiliation.findall(entry)]
    return {"name":name,"affiliations":affiliations}

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
  sample="http://www.biomedcentral.com/1471-2415/12/36/"
  sample2="http://www.biomedcentral.com/1471-2377/12/93/"
  art=Article(sample)
  print art.get_authors()
