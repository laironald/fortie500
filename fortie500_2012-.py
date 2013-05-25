import csv
import codecs
import BeautifulSoup
import urllib2

years = range(2006, 2013, 1)
years = range(2009, 2013, 1)
max_f1000 = 2009

pages = ["index"]
pages.extend(["{0}_{1}".format(100*x+1, 100*(x+1)) for x in range(1,10)])

baseurl = "http://money.cnn.com/magazines/fortune/fortune500/{year}/full_list/{page}.html"
linkurl = "http://money.cnn.com/magazines/fortune/fortune500/{year}/{page}"
linkurl2 = "http://money.cnn.com/{page}"

for year in years:
    print year
    out = codecs.open("output/f500-{year}.txt".format(year=year), encoding="utf-8", mode="wb")
    out.write(u"rank\turl\tcompany\n")
    
    for j,page in enumerate(pages):
        if year > max_f1000 and j > 4:
            break
            
    
        url = baseurl.format(year=year, page=page)
        html = urllib2.urlopen(url)
        html = "".join([x for x in html])
        
        soup = BeautifulSoup.BeautifulSoup(html)
        tables = soup.findAll("table")
        for table in tables:
            if not table.get("class"):
                continue
            if "cnnwith220inset" in table.get("class").split() or \
               "with220inset"    in table.get("class").split() or \
               "maglisttable"    in table.get("class").split():
                for td in table.findAll("td"):
                    if td.get("class") in ("cnncol1", "alignRgt", "rank"):
                        out.write(td.text)
                        out.write("\t")
                    elif td.get("class") in ("cnncol2", "alignLft", "company"):
                        page = page=td.findChild("a")["href"]
                        if page[:2] == "..":
                            out.write(linkurl.format(year=year, page=page[3:]))
                        elif page[0] == "/":
                            out.write(linkurl2.format(page=page[1:]))
                        out.write("\t")
                        out.write(td.text)
                        out.write("\n")
