import sqlite3
import urllib2
import unidecode
import bs4
import time
import re


boardURL = "http://www.reuters.com/finance/stocks/companyOfficers?symbol={}"

conn = sqlite3.connect('f500.db')
conn.text_factory = str
c = conn.cursor()
c.executescript("""
    PRAGMA encoding = "UTF-8";
    CREATE TABLE IF NOT EXISTS f500_person_object (
        person_id       VARCHAR,
        name__first     VARCHAR,
        name__last      VARCHAR,
        age             INTEGER,
        gender          VARCHAR,
        biography       TEXT);
    CREATE UNIQUE INDEX IF NOT EXISTS
        idx_idx6 ON f500_person_object (person_id);

    CREATE TABLE IF NOT EXISTS f500_person_company_link (
        person_id       VARCHAR,
        company_id      VARCHAR,
        since,          INTEGER,
        position,       VARCHAR,
        seq_num         INTEGER);
    CREATE INDEX IF NOT EXISTS
        idx_idx7 ON f500_person_company_link (company_id);
    CREATE INDEX IF NOT EXISTS
        idx_idx8 ON f500_person_company_link (person_id);
    CREATE INDEX IF NOT EXISTS
        idx_idx9 ON f500_person_company_link (company_id, person_id);
    """)


def getGender(biography):
    if not biography:
        return ""
    elif biography[:3] == "Mr.":
        return "Male"
    elif biography[:3] == "Ms.":
        return "Female"
    else:
        ms = len(re.findall(r'\b(he|his)\b', biography, re.I))
        fs = len(re.findall(r'\b(she|her)\b', biography, re.I))
        if not (ms or fs):
            return ""
        if ms > fs:
            return "Male"
        else:
            return "Female"


def getBoard(ticker):
    c.execute("""
        SELECT  count(*)
          FROM  f500_person_company_link
         WHERE  company_id = ?
         """, (ticker,))
    if c.fetchone()[0] > 0:
        return
    print ticker
    try:
        res = urllib2.urlopen(boardURL.format(ticker))
    except:
        print "500 error?"
        return
    res = "".join([r for r in res])
    res = res.replace('"image""cl', '"image" cl')
    soup = bs4.BeautifulSoup(res)

    person = {}
    tables = soup.find_all("table")
    if len(tables) != 5:
        print "strange"
        return
    for i, tbl in enumerate(tables[:2]):
        if i == 0:
            for tr in tbl.find_all("tr"):
                tds = tr.find_all("td")
                if tds:
                    person_id = tds[0].a.get("href").split("=")[-1]
                    person[person_id] = {}
                    peep = person[person_id]
                    peep["name"] = tds[0].get_text().split(u'\xa0')
                    peep["age"] = tds[1].get_text()
                    if peep["age"]:
                        peep["age"] = int(peep["age"])
                    peep["since"] = tds[2].get_text()
                    if peep["since"]:
                        peep["since"] = int(peep["since"])
                    peep["position"] = tds[3].get_text()
        elif i == 1:
            for tr in tbl.find_all("tr"):
                tds = tr.find_all("td")
                if tds:
                    person_id = tds[0].a.get("href").split("=")[-1]
                    person[person_id]["bio"] = unidecode.unidecode(tds[1].get_text().replace(u"\u2013", "-"))

    for seq, p in enumerate(person):
        cp = person[p]
        c.execute("""
            INSERT OR IGNORE INTO f500_person_object
            (person_id, name__first, name__last, age, gender, biography)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (p, cp["name"][0], cp["name"][1], cp["age"], getGender(cp["bio"]), cp["bio"]))
        c.execute("""
            INSERT OR IGNORE INTO f500_person_company_link
            (person_id, company_id, since, position, seq_num)
            VALUES (?, ?, ?, ?, ?)
            """, (p, ticker, cp["since"], cp["position"], seq))

    conn.commit()
    time.sleep(0.5)

c.execute("""
    SELECT  company_id
      FROM  f500_company_object
    """)
for ticker in c.fetchall():
    getBoard(ticker[0])

conn.commit()
conn.close()
