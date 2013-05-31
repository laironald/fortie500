import os
import re
import sqlite3

conn = sqlite3.connect('f500.db')
conn.text_factory = str
c = conn.cursor()
c.executescript("""
  PRAGMA encoding = "UTF-8";
  CREATE TABLE IF NOT EXISTS f500_company_object (
    company_id      INTEGER PRIMARY KEY,
    name            VARCHAR,
    ticker          VARCHAR);
  CREATE UNIQUE INDEX IF NOT EXISTS
    idx_idx ON f500_company_object (company_id);
  CREATE UNIQUE INDEX IF NOT EXISTS
    idx_idx1 ON f500_company_object (name);

  CREATE TABLE IF NOT EXISTS f500_company_year_link (
    company_id      INTEGER,
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


def parseFile(fname):
    f = open("output/"+fname)
    year_id = fname[-8:-4]
    for i, row in enumerate(f.read().split("\n")):
        if i == 0 or not row:
            continue
        row = re.sub(" *[\t] *", "\t", row).strip()
        row = row.replace("&amp;", "&")
        seq, url, comp = row.split("\t")
        finder = re.findall("(.*?)[(](.*?)[)]", comp)
        ticker = ""
        if finder:
            comp, ticker = finder[0]
        companies = i
        c.execute("""
            INSERT OR IGNORE INTO f500_company_object
              (name, ticker) VALUES (?, ?)
            """, (comp, ticker))
        c.execute("""
            SELECT  company_id
              FROM  f500_company_object
             WHERE  name = ?
            """, (comp,))
        company_id = c.fetchone()[0]
        c.execute("""
            INSERT OR IGNORE INTO f500_company_year_link
              (company_id, year_id, seq_num, url__fortune) VALUES (?, ?, ?, ?)
            """, (company_id, year_id, i, url))

    c.execute("""
        INSERT OR IGNORE INTO f500_year_legend
          (year_id, companies) VALUES (?, ?)
        """, (year_id, companies))
    f = None

parseFile(fname="f500-2006.txt")
for fname in os.listdir("output"):
    parseFile(fname=fname)

conn.commit()
conn.close()
