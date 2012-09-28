import couchdb.client
import json

db=couchdb.client.Database("biomedcentral")

result=db.view("_all_docs",limit=1000)
while (result.rows):
  print result.rows[0].id
  f=open("export/%s.json"%result.rows[0].id,"w")
  rows=[r.id for r in result.rows]
  json.dump([db[id] for id in rows],f)
  f.close()
  result=db.view("_all_docs",limit=1000,startkey_docid=rows[-1])
