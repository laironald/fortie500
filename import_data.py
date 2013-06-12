import os
import re
import sqlite3
import urllib
import urllib2
import unidecode
import json
import time


tickerURL = "https://www.google.com/finance/match?matchtype=matchall&{0}"

conn = sqlite3.connect('f500.db')
conn.text_factory = str
c = conn.cursor()
c.executescript("""
    PRAGMA encoding = "UTF-8";
    CREATE TABLE IF NOT EXISTS f500_company_object (
        company_id      VARCHAR,
        name            VARCHAR,
        ticker          BOOLEAN);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idx ON f500_company_object (company_id);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idx1 ON f500_company_object (name);


    CREATE TABLE IF NOT EXISTS f500_company_year_link (
        company_id      VARCHAR,
        year_id         INTEGER,
        seq_num         INTEGER,
        url__fortune    VARCHAR);
    CREATE INDEX IF NOT EXISTS
        idx_idx2 ON f500_company_year_link (company_id);
    CREATE INDEX IF NOT EXISTS
        idx_idx3 ON f500_company_year_link (year_id);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idx4 ON f500_company_year_link (company_id, year_id);


    CREATE TABLE IF NOT EXISTS f500_year_legend (
        year_id         INTEGER,
        companies       INTEGER);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idx5 ON f500_year_legend (year_id);
    """)


c.execute("""
    SELECT  name, company_id
      FROM  f500_company_object
    """)
tickers = dict(c.fetchall())
tcounter = 0


def getTicker(comp):
    if comp not in tickers:
        q = unidecode.unidecode(comp)
        qs = urllib.urlencode({"q": q})
        res = urllib2.urlopen(tickerURL.format(qs))
        res = json.loads("".join([r for r in res]))
        if res['matches'] and res['matches'][0]['t']:
            res = res['matches'][0]
            res = res['t']
        else:
            res = "--{}".format(comp)
        time.sleep(0.5)
        tickers[comp] = res
        print "fetch: ", res, len(tickers)
    return tickers[comp]


def parseFile(fname):
    print fname
    f = open("output/"+fname)
    year_id = fname[-8:-4]
    for i, row in enumerate(f.read().split("\n")):
        if i == 0 or not row:
            continue
        row = re.sub(" *[\t] *", "\t", row).strip()
        row = row.replace("&amp;", "&")
        row = row.replace("&quot;", '"')
        seq, url, comp = row.split("\t")
        finder = re.findall("(.*?)[(](.*?)[)]", comp)
        company_id = ""
        if finder:
            comp, company_id = finder[0]
            tickers[comp] = company_id
        else:
            company_id = getTicker(comp)

        companies = i
        if company_id[:2] == "--":
            ticker = False
        else:
            ticker = True

        c.execute("""
            INSERT OR IGNORE INTO f500_company_object
              (company_id, name, ticker) VALUES (?, ?, ?)
            """, (company_id, comp, ticker))
        c.execute("""
            INSERT OR IGNORE INTO f500_company_year_link
              (company_id, year_id, seq_num, url__fortune) VALUES (?, ?, ?, ?)
            """, (company_id, year_id, i, url))

    c.execute("""
        INSERT OR IGNORE INTO f500_year_legend
          (year_id, companies) VALUES (?, ?)
        """, (year_id, companies))
    f = None
    conn.commit()

parseFile(fname="f500-2006.txt")
for fname in os.listdir("output"):
    parseFile(fname=fname)

conn.commit()
conn.close()
