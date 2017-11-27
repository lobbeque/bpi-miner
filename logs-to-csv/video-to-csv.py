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
step     = 2000;

# Delete and create corresponding csv

try:
    os.remove("logs-bpi-video-" + fromDate + "-" + toDate + ".csv")
except OSError:
    pass

csv    = open("logs-bpi-video-" + fromDate + "-" + toDate + ".csv", "w") 
header = "session_id;timestamp;domain;url;title\n"
csv.write(header)

def writeCsv(id,time,domain,url,title):
	print(url)
	row = id + ";" + time + ";" + str(domain) + ";" + url + ";" + title + "\n";
	try:
		csv.write(row)
		# print(row)
	except:
		try:
			title = unicodedata.normalize('NFD', title).encode('ascii', 'ignore')
			row = id + ";" + time + ";" + str(domain) + ";" + url + ";" + title + "\n";
			csv.write(row)
		except:
			print("shit")

def extract( domain, url, id, time ):

	if "proxy" in url or "live.isml" in url:
		return
	
	if "embed" in url:
		url = re.sub(r"embed\/", "", url)

	try :
		html = urlopen(url,data=None,timeout=10).read()
	except :
		# print("==============")
		# print(url)
		return

	soup = BeautifulSoup.BeautifulSoup(html)
	title = soup.title

	if title is None or title == "":
		return
	writeCsv(id,time,domain,url,title.string)

				

host = "http://10.1.2.54:9200"

print("\n== Get Number of logs between " + fromDate + " and " + toDate + " ==")

path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20catolfeo%3A1207%20AND%20domain%3A*dailymotion*&size=0"

print(path)

r    = requests.get(path)
data = json.loads(r.text)
nb   = data["hits"]["total"]
rng  = range(0,nb,step)

print(nb)

for i in rng:
	print("\n== Get logs from " + str(i) + " to " + str(i + step) + " ==")
	fl   = "&fields=session_uid,@timestamp,domain,url"
	path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20catolfeo%3A1207%20AND%20domain%3A*dailymotion*" + fl + "&size=" + str(step) + "&from=" + str(i)
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

		if "video" in url:
			# print(logs.index(log))
			extract(dom, url, f.get("session_uid","null")[0], f.get("@timestamp","null")[0])
