import csv
import codecs
import BeautifulSoup
import urllib2

years = range(2006, 2013, 1)
max_f1000 = 2010

pages = ["index"]
pages.extend(["{0}_{1}".format(100*x+1, 100*(x+1)) for x in range(1,10clea)])

baseurl = "http://money.cnn.com/magazines/fortune/fortune500/{year}/full_list/{page}.html"

for year in years:
    for j,page in enumerate(pages):
        if year > max_f1000 and j > 4:
            break
        url = baseurl.format(year=year, page=page)

"""
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
"""
