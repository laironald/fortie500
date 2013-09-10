import csv
import re
import sqlite3
import urllib
import urllib2
import unidecode
import json
import glob
import time


tickerURL = "https://www.google.com/finance/match?matchtype=matchall&{0}"
gfinURL = "https://www.google.com/finance?q={}"

conn = sqlite3.connect('f500.db')
conn.text_factory = str
c = conn.cursor()
c.executescript("""
    PRAGMA encoding = "UTF-8";
    CREATE TABLE IF NOT EXISTS companyHash (
        company_id      VARCHAR,
        name            VARCHAR,
        name_decode     VARCHAR,
        ticker          BOOLEAN);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idxc1 ON companyHash (name);
    CREATE TABLE IF NOT EXISTS pageHash (
        url             VARCHAR,
        content         TEXT);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idxc2 ON pageHash (url);

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
    CREATE INDEX IF NOT EXISTS
        idx_idx4 ON f500_company_year_link (company_id, year_id);


    CREATE TABLE IF NOT EXISTS f500_year_legend (
        year_id         INTEGER,
        companies       INTEGER);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idx5 ON f500_year_legend (year_id);
    """)


c.execute("""
    SELECT  name, company_id, name_decode
      FROM  companyHash
    """)
tickers = dict([[x, x[1:]] for x in c.fetchall()])
tcounter = 0


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


def getTicker(comp):
    if comp not in tickers:
        q = unidecode.unidecode(comp.decode("latin-1"))
        qs = urllib.urlencode({"q": q})
        res = json.loads(getUrl(tickerURL.format(qs)))
        if res['matches'] and res['matches'][0]['t']:
            res = res['matches'][0]
            company_id = res['t']
            name_decode = res['n']
        else:
            company_id = ""
            name_decode = ""
        tickers[comp] = [company_id, name_decode]
        print "fetch: ", company_id, len(tickers)
    return tickers[comp]


def parseFile(fname, year_id=None):
    print fname
    if not year_id:
        year_id = fname[-8:-4]

    f = open(fname, "rb")
    if fname[-3:] == "txt":
        format = "txt"
        lines = f.read().split("\n")
    elif fname[-3:] == "csv":
        format = "csv"
        lines = csv.reader(f)

    for i, row in enumerate(lines):
        if i == 0 or not row:
            continue
        if format == "txt":
            row = re.sub(" *[\t] *", "\t", row).strip()
            row = row.replace("&amp;", "&")
            row = row.replace("&quot;", '"')
            seq, url, name = row.split("\t")
        elif format == "csv":
            seq, name = row[:2]
            url = ""

        finder = re.findall("(.*?)[(](.*?)[)]", name)
        if finder:
            name = finder[0][0]
            company_id, name_decode = getTicker(finder[0][1])
        else:
            company_id, name_decode = getTicker(name)
        if not company_id and len(name) > 10:
            company_id, name_decode = getTicker(name[:len(name)/2])

        if not company_id:
            ticker = False
        else:
            ticker = True

        c.execute("""
            INSERT OR IGNORE INTO companyHash
                (company_id, name, name_decode, ticker)
                VALUES (?, ?, ?, ?)
            """, (company_id, name, name_decode, ticker))
        c.execute("""
            UPDATE  companyHash
               SET  company_id = "|"||ROWID||"|"
             WHERE  company_id = ""
            """)
        c.execute("""
            SELECT  company_id
              FROM  companyHash
             WHERE  name = ?
            """, (name,))
        company_id = c.fetchone()[0]
        c.execute("""
            INSERT OR IGNORE INTO f500_company_year_link
              (company_id, year_id, seq_num, url__fortune) VALUES (?, ?, ?, ?)
            """, (company_id, year_id, seq, url))
        if i % 20 == 0:
            conn.commit()

        #c.execute("""
        #    INSERT OR IGNORE INTO f500_company_object
        #      (company_id, name, ticker) VALUES (?, ?, ?)
        #    """, (company_id, comp, ticker))

    c.execute("""
        REPLACE INTO f500_year_legend
          (year_id, companies) VALUES (?, ?)
        """, (year_id, seq))
    f = None
    conn.commit()

parseFile(fname="output/f500-2006.txt")
for fname in glob.glob("output/*.txt"):
    parseFile(fname=fname)
# parseFile(fname="output/2013-SK.csv", year_id="2013_new")
parseFile(fname="output/f1000-2013.csv", year_id="2013")


conn.commit()
conn.close()
