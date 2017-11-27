import sys
import requests
import json
import os

if len(sys.argv) < 2:
    sys.exit('Usage: %s from to' % sys.argv[0])

fromDate = str(sys.argv[1])
toDate   = str(sys.argv[2])
step     = 10000;

# Delete and create corresponding csv

try:
    os.remove("logs-bpi-full-" + fromDate + "-" + toDate + ".csv")
except OSError:
    pass

csv    = open("logs-bpi-full-" + fromDate + "-" + toDate + ".csv", "w") 
header = "session_id;timestamp;domain;domain2;url;computer_id;geo1;geo2;geo3;res;computer_profil;computer_sector;catolfeo\n"
csv.write(header)

host = "http://10.1.2.54:9200"

print("\n== Get Number of logs between " + fromDate + " and " + toDate + " ==")

path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20NOT%20catolfeo%3A1000&size=0"

print(path)

r    = requests.get(path)
data = json.loads(r.text)
nb   = data["hits"]["total"]
rng  = range(0,nb,step)

print(nb)

for i in rng:
	print("\n== Get logs from " + str(i) + " to " + str(i + step) + " ==")
	fl   = "&fields=session_uid,@timestamp,domain,domain2,url,poste_id,geo1,geo2,geo3,res,poste_profil,poste_sector,catolfeo,catolfeo_explained"
	path = host + "/bpi_logs-*/_search?q=@timestamp:[" + fromDate + "%20TO%20" + toDate + "]%20AND%20NOT%20catolfeo%3A1000" + fl + "&size=" + str(step) + "&from=" + str(i)
	print(path)
	r    = requests.get(path)
	data = json.loads(r.text)
	logs = data["hits"]["hits"]
	for log in logs:
		f   = log["fields"]
		row = str(f.get("session_uid","null")[0]) + ";" + f.get("@timestamp","null")[0] + ";" + str(f.get("domain","null")[0]) + ";" + str(f.get("domain2","null")[0]) + ";" + f.get("url","null")[0] + ";" + f.get("poste_id")[0] + ";" + str(f.get("geo1","null")[0]) + ";" + str(f.get("geo2","null")[0]) + ";" + str(f.get("geo3","null")[0]) + ";" + str(f.get("res","null")[0]) + ";" + str(f.get("poste_profil","null")[0]) + ";" + str(f.get("poste_sector","null")[0]) + ";" + str(f.get("catolfeo","null")[0]) + ";" + "\n"
		try:
			csv.write(row)
		except:
			print("shit")
