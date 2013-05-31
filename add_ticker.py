import sqlite3
import urllib
import urllib2
import json
import time
import unidecode

baseURL = "https://www.google.com/finance/match?matchtype=matchall&{0}"
conn = sqlite3.connect('f500.db')
c = conn.cursor()

c.execute("""
    SELECT  company_id, name
      FROM  f500_company_object
     WHERE  ticker = "-"
    """)
comps = c.fetchall()

print "Tickers:", len(comps)
for i, v in enumerate(comps):
    n, q = v
    q = unidecode.unidecode(q)
    qs = urllib.urlencode({"q": q})
    res = urllib2.urlopen(baseURL.format(qs))
    res = json.loads("".join([r for r in res]))
    if res['matches'] and res['matches'][0]['t']:
        res = res['matches'][0]
        print " * {}-{})".format(i, n), q, "--", \
              res['n'], "({})".format(res['t'])
        res = res['t']
    else:
        res = "-"
    c.execute("""
        UPDATE f500_company_object SET ticker = ? WHERE company_id = ?
        """, (res, n))
    time.sleep(0.2)

conn.commit()
conn.close()
