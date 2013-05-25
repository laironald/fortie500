import csv
import BeautifulSoup
import urllib2

data = {2013:"http://money.cnn.com/magazines/fortune/fortune500/2013/full_list/index.html?iid=F500_sp_full"}

html = urllib2.urlopen(data[2013])
html = "".join([x for x in html])

soup = BeautifulSoup.BeautifulSoup(html)
soup = soup.find(id="f500-list")

cnt = 0
for span in soup.findAll("span"):
    if "name" in span['class'].split():
        cnt += 1
        print cnt, span.text


