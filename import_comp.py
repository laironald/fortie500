import re
import sqlite3
import urllib
import urllib2
import json
import glob
import time


tickerURL = "https://www.google.com/finance/match?matchtype=matchall&{0}"
gfinURL = "https://www.google.com/finance?q={}"
raw_company = []

conn = sqlite3.connect('f500.db')
conn.text_factory = str
c = conn.cursor()


def getUrl(url):
    c.execute("""
        SELECT content FROM pageHash WHERE url=?
        """, (url,))
    content = c.fetchone()
    if not content:
        res = urllib2.urlopen(url)
        content = "".join([r for r in res])
        c.execute("""
            INSERT OR IGNORE INTO pageHash
            (url, content) VALUES (?, ?)
            """, (url, content))
        time.sleep(0.5)
    else:
        content = content[0]
    return content


def getName(ticker):
    qs = urllib.urlencode({"q": ticker})
    res = json.loads(getUrl(tickerURL.format(qs)))
    if res['matches'] and res['matches'][0]['t']:
        res = res['matches'][0]
        name_decode = res['n']
    else:
        name_decode = ""
    print name_decode
    return name_decode


def companyFix(fname):
    if not raw_company:
        c.execute("""
            SELECT rowid, * FROM companyHash
            """)
        raw_company.extend(c.fetchall())

    f = open(fname, 'rb')
    comp_convert = {}
    for r in f:
        r = re.sub(" +", " ", r)
        k, v = r[:-1].split(" ")
        comp_convert[k] = v

    for raw in raw_company:
        key = "|{0}|".format(raw[0])
        val = comp_convert.get(key)
        if val and raw[1] != val:
            if val[0] == "|":
                c.execute("""
                    UPDATE  companyHash
                       SET  company_id = ?, name_decode = "", ticker = 0
                     WHERE  rowid = ?
                    """, (val, raw[0]))
            else:
                c.execute("""
                    UPDATE  companyHash
                       SET  company_id = ?, name_decode = ?, ticker = 1
                     WHERE  rowid = ?
                    """, (val, getName(val), raw[0]))

            print comp_convert[key]
    conn.commit()


for fname in glob.glob("output/company_fix_*"):
    companyFix(fname=fname)


conn.commit()
conn.close()