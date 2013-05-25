import urllib2
data = {2013:"http://money.cnn.com/magazines/fortune/fortune500/2013/full_list/index.html?iid=F500_sp_full"}

html = urllib2.urlopen(data[2013])
html = [x for x in html]
