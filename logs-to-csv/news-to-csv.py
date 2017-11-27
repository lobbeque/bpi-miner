import sys
import requests
import json
import os
import re
from urllib2 import urlopen
import bs4 as BeautifulSoup
import unicodedata

if len(sys.argv) < 2:
    sys.exit('Usage: %s from to' % sys.argv[0])

fromDate = str(sys.argv[1])
toDate   = str(sys.argv[2])
step     = 5000;

# Delete and create corresponding csv

try:
    os.remove("logs-bpi-news-" + fromDate + "-" + toDate + ".csv")
except OSError:
    pass

csv    = open("logs-bpi-news-" + fromDate + "-" + toDate + ".csv", "w") 
header = "timestamp;domain;extension;title;url\n"
csv.write(header)

def writeCsv(id,time,domain,url,title,extension):
	print(title)
   	row = time + ";" + str(domain) + ";" + extension + ";" + title.replace(";", " ") + ";" + url + "\n";
	try:
		csv.write(row)
		# print(row)
	except:
		try:
			title = unicodedata.normalize('NFD', title).encode('ascii', 'ignore')
			row = time + ";" + str(domain) + ";" + extension + ";" + title.replace(";", " ") + ";" + url + "\n";
			csv.write(row)
		except:
			print("shit")

def extract( domain, url, id, time, extension ):
	uri = url.split('/')
	title = uri[len(uri)-1]
	if title == "":
		title = uri[len(uri)-2]

	if "=" in title:
		return

	if title.isdigit():
		return
	
	try :
		html = urlopen(url,data=None,timeout=10).read()
	except :
		return
	
	soup = BeautifulSoup.BeautifulSoup(html)
	title = soup.title

	try:
		if title is None or title.string.strip() == "":
			return
	except:
		return

	writeCsv(id,time,domain,url,title.string.strip(), extension)
				

host = "http://10.1.2.54:9200"

print("\n== Get Number of logs between " + fromDate + " and " + toDate + " ==")

path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20catolfeo%3A51&size=0"

print(path)

r    = requests.get(path)
data = json.loads(r.text)
nb   = data["hits"]["total"]
rng  = range(0,nb,step)

print(nb)

for i in rng:
	print("\n== Get logs from " + str(i) + " to " + str(i + step) + " ==")
	fl   = "&fields=session_uid,@timestamp,domain,url,extension"
	path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20catolfeo%3A51" + fl + "&size=" + str(step) + "&from=" + str(i)
	print(path)
	r    = requests.get(path)
	data = json.loads(r.text)
	logs = data["hits"]["hits"]
	for log in logs:
		f   = log["fields"]
		url = f.get("url","null")[0]
		dom = f.get("domain","null")[0]

		if "https" in url:
			continue
		
		if ".JPG" in url or ".PNG" in url or ".mp4" in url or ".MP4" in url or ".png" in url or ".jpg" in url:
			continue

		if "2017" in url or "2016" in url or "2015" in url:
			extract(dom, url, f.get("session_uid","null")[0], f.get("@timestamp","null")[0], f.get("extension","null")[0])
