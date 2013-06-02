import codecs
import bs4
import urllib2

url = "http://money.cnn.com/magazines/fortune/fortune500/2013/full_list/index.html?iid=F500_sp_full"
baseurl = "http://money.cnn.com"

html = urllib2.urlopen(url)
html = "".join([x for x in html])

soup = bs4.BeautifulSoup(html)
soup = soup.find(id="f500-list")
soup = soup.find(id="content-placeholder")

cnt = 0
out = codecs.open("output/f500-2013.txt", encoding="utf-8", mode="wb")
out.write("rank\turl\tcompany\n")
for li in soup.findAll("li"):
    cnt += 1
    out.write(u"{0}\t".format(cnt))
    out.write(u"{0}\t".format(baseurl+li.findChild("a")["href"]))
    for span in li.findAll("span"):
        if "name" in span['class'].split():
            out.write(u"{0}\n".format(span.text))
            continue

out = None
