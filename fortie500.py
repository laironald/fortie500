import csv
import codecs
import BeautifulSoup
import urllib2

url = {2013:"http://money.cnn.com/magazines/fortune/fortune500/2013/full_list/index.html?iid=F500_sp_full"}

html = urllib2.urlopen(url[2013])
html = "".join([x for x in html])

soup = BeautifulSoup.BeautifulSoup(html)
soup = soup.find(id="f500-list")

cnt = 0
out = codecs.open("output/f500-2013.txt", encoding="utf-8", mode="wb")
data = [["number", "company"]]
for span in soup.findAll("span"):
    if "name" in span['class'].split():
        cnt += 1
        out.write(u"{0}\t{1}\n".format(cnt, span.text))

out = None
