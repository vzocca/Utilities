# -*- coding: utf-8 -*-

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://inducks.org/recommend.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch(page):
    r = requests.get(
        URL,
        params={"top100": 1, "page": page},
        headers=HEADERS,
        timeout=30
    )
    r.raise_for_status()
    return r.text


def is_valid_rank(x):
    return x.isdigit()


def parse(html, page):
    soup = BeautifulSoup(html, "lxml")

    data = []

    for tr in soup.find_all("tr"):
        cols = tr.find_all("td")
        if len(cols) < 3:
            continue

        text = [c.get_text(" ", strip=True) for c in cols]

        rank = text[0]
        code = text[1]

        # FILTRO CHIAVE REALE
        # rank deve essere numero
        if not rank.isdigit():
            continue

        # codice INDUCKS ha sempre almeno una lettera
        if not any(c.isalpha() for c in code):
            continue

        data.append({
            "page": page,
            "rank": int(rank),
            "code": code,
            "title": text[2],
            "author": text[3] if len(text) > 3 else None,
            "extra": " | ".join(text[4:]) if len(text) > 4 else None
        })

    return data


def main():
    all_rows = []
    page = 0

    while True:
        print("page", page)

        html = fetch(page)
        rows = parse(html, page)

        print("rows:", len(rows))

        if not rows:
            break

        all_rows.extend(rows)

        page += 1
        time.sleep(1)

    df = pd.DataFrame(all_rows)
    df.to_csv("inducks_top100.csv", index=False, encoding="utf-8-sig")

    print("DONE:", len(df))


if __name__ == "__main__":
    main()