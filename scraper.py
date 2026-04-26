import os
import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup


URL = "https://www.boxofficemojo.com/chart/top_lifetime_gross/"
DATA_FILE = "data/filmes.json"

os.makedirs("data", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(URL, headers=headers, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

filmes = []
vistos = set()

for link in soup.find_all("a", href=True):
    href = link["href"]
    title = link.get_text(strip=True)

    if "/title/tt" in href and title and title not in vistos:
        registo = {
            "title": title,
            "source": "boxofficemojo",
            "rating": None,
            "votes": None,
            "genre": [],
            "timestamp": datetime.now().isoformat()
        }

        filmes.append(registo)
        vistos.add(title)

    if len(filmes) >= 10:
        break

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(filmes, f, ensure_ascii=False, indent=4)

print("Filmes encontrados:", len(filmes))