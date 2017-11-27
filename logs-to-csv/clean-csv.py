import sys
import requests
import json
import os
import re
from urllib2 import urlopen
import bs4 as BeautifulSoup
import unicodedata

if len(sys.argv) < 1:
    sys.exit('Usage: %s from to' % sys.argv[0])

fname  = str(sys.argv[1])

with open(fname) as f:
    content = f.readlines()

try:
    os.remove(fname)
except OSError:
    pass

csv = open(fname, "w") 

for line in content :
	cells = line.split(';')
	print(line)
	if len(cells) == 5:
		csv.write(cells[0] + ";" + cells[1] + ";" + cells[2] + ";" + cells[3] + ";" + cells[4])
	elif len(cells) == 6:
		csv.write(cells[0] + ";" + cells[1] + ";" + cells[2] + ";" + cells[3] + ";" + cells[5])
