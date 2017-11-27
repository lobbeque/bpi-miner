import sys
import requests
import json
import os
import re
from urllib2 import urlopen
import bs4 as BeautifulSoup
import unicodedata
import urllib

if len(sys.argv) < 2:
    sys.exit('Usage: %s from to' % sys.argv[0])

fromDate = str(sys.argv[1])
toDate   = str(sys.argv[2])
step     = 100;

# Delete and create corresponding csv

try:
    os.remove("logs-bpi-traduction-" + fromDate + "-" + toDate + ".csv")
except OSError:
    pass

csv    = open("logs-bpi-traduction-" + fromDate + "-" + toDate + ".csv", "w") 
header = "session_id;timestamp;domain;url;from;to;query\n"
csv.write(header)

def writeCsv(id,time,domain,url,f,t,q):
	if q is None:
		return
	if q == "":
		return
	q = q.replace("+"," ") 
	q = q.replace("%20", " ").replace("%C3%A9", "e").replace("%0A", "").replace("%C3%A4","a").replace("%C3%A7","c").replace("%27"," ").replace("%C3%AA","e")
	q = q.replace("%C3%A0","a").replace("%C3%B9","u").replace("%C3%A8","e").replace("%C3%BC","u").replace("%C3%A2","a")
	q = unicodedata.normalize('NFD', q).encode('ascii', 'ignore')
	q = q.strip()
	if q == "":
		return
	print(q)
	row = id + ";" + time + ";" + str(domain) + ";" + url + ";" + f + ";" + t + ";" + q + "\n";
	csv.write(row)

def extractLinguee( domain, url, id, time ):
	# print(url)
	uri = url.split("/")
	if ".mp4" in url or uri[3] == "":
		return
	if "qe=" in url:
		f   = uri[3].split("-")[0]
		t   = uri[3].split("-")[1]
		q = uri[4].split("&")[0].replace("search?qe=","")
		writeCsv(id,time,domain,url,f,t,q)
	elif "query=" in url:
		f   = uri[3].split("-")[0]
		t   = uri[3].split("-")[1]
		q = uri[4].split("&")[1].replace("query=","")
		writeCsv(id,time,domain,url,f,t,q)		
	else:
		if len(uri) != 6:
			return
		f   = uri[3].split("-")[0]
		t   = uri[3].split("-")[1]
		q   = uri[5].split(".")[0]
		writeCsv(id,time,domain,url,f,t,q)


def extractReversoDico( domain, url, id, time ):
	if "synonymes" in url or "definition" in url or "Captcha.aspx" in url:
		return

	# print(url)
	uri = url.split("/")
	if (len(uri) == 5 and "Interface" not in uri[3]):
		f   = uri[3].split("-")[0]
		t   = uri[3].split("-")[1]
		q   = uri[4]
		writeCsv(id,time,domain,url,f,t,q)
	elif ("source" in uri[3] and "target" in uri[3] and "searchWorld" in uri[3]):
		tmp = uri[3].split("&")
		f   = re.sub(r"(.*)source=", "", tmp[0])
		t   = re.sub(r"(.*)target=", "", tmp[1])
		q   = re.sub(r"(.*)searchWorld=", "", tmp[2])
		writeCsv(id,time,domain,url,f,t,q)

def extractReversoCtx( domain, url, id, time ):
	if "contexticons" in url:
		return

	# print(url)
	uri = url.split("/")
	if (len(uri) == 5 and uri[4] != ""):
		f   = uri[3].split("-")[0]
		t   = uri[3].split("-")[1]
		q   = uri[4]
		writeCsv(id,time,domain,url,f,t,q)
	elif ("source" in uri[3] and "target" in uri[3]):
		tmp = uri[3].split("&")
		f   = re.sub(r"(.*)source_lang=", "", tmp[1])
		t   = re.sub(r"(.*)target_lang=", "", tmp[2])
		q   = re.sub(r"(.*)source_text=", "", tmp[0])
		writeCsv(id,time,domain,url,f,t,q)

def extractWordreference( domain, url, id, time ):
	if "synonymes" in url or "definition" in url:
		return

	uri = url.split("/")

	if "translation.aspx" in url:
		tmp = url.split("?")[1].split("&")
		ft  = re.sub(r"(.*)dict=", "", tmp[1])
		f,t = ft[:len(ft)/2], ft[len(ft)/2:]
		q   = re.sub(r"(.*)w=", "", tmp[0])
		writeCsv(id,time,domain,url,f,t,q)
	elif (len(uri) == 5 and uri[4] != ""):
		f,t = uri[3][:len(uri[3])/2], uri[3][len(uri[3])/2:]
		q   = uri[4]
		writeCsv(id,time,domain,url,f,t,q)
	elif (len(uri) == 6 and "dict" in uri[5] and "query" in uri[5]):
		tmp = uri[5].split("&")
		ft  = re.sub(r"(.*)dict=", "", tmp[0])
		f,t = ft[:len(ft)/2], ft[len(ft)/2:]
		q   = re.sub(r"(.*)query=", "", tmp[1])
		writeCsv(id,time,domain,url,f,t,q)

tradDomains = ["linguee","dictionnaire.reverso","context.reverso","wordreference.com"]
tradExtract = [extractLinguee,extractReversoDico,extractReversoCtx,extractWordreference]

def extract( domain, url, id, time ):
	for tradDom in tradDomains:
		if tradDom in domain:
			tradExtract[tradDomains.index(tradDom)](domain, url, id, time)
			continue	

host = "http://10.1.2.54:9200"

print("\n== Get Number of logs between " + fromDate + " and " + toDate + " ==")

path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20catolfeo%3A1222%20AND%20NOT%20domain%3A*google*&size=0"

print(path)

r    = requests.get(path)
data = json.loads(r.text)
nb   = data["hits"]["total"]
rng  = range(0,nb,step)

print(nb)

for i in rng:
	print("\n== Get logs from " + str(i) + " to " + str(i + step) + " ==")
	fl   = "&fields=session_uid,@timestamp,domain,url"
	path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20catolfeo%3A1222%20AND%20NOT%20domain%3A*google*" + fl + "&size=" + str(step) + "&from=" + str(i)
	print(path)
	r    = requests.get(path)
	data = json.loads(r.text)
	logs = data["hits"]["hits"]
	for log in logs:
		f   = log["fields"]
		url = f.get("url","null")[0]
		dom = f.get("domain","null")[0]
		extract(dom, url, f.get("session_uid","null")[0], f.get("@timestamp","null")[0])
