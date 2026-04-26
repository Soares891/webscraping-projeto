import os
import re
import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup


URL = "https://www.rottentomatoes.com/browse/movies_at_home/sort:popular"
DATA_FILE = "data/filmes.json"
LOG_FILE = "logs/scraper.log"

os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def limpar_titulo(title):
    title = title.strip()
    title = re.sub(r"^Watch the trailer for\s+", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


def main():
    logging.info("Início do scraping Rotten Tomatoes")

    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pattern = r"(?:(\d{1,3})%\s+)?(?:(\d{1,3})%\s+)?(.+?)\s+Streaming\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}"

    matches = re.findall(pattern, text)

    filmes = []
    vistos = set()

    for critic_score, audience_score, title in matches:
        title = limpar_titulo(title)

        if not title or title in vistos:
            continue

        rating = int(critic_score) if critic_score else None
        votes = int(audience_score) if audience_score else None

        registo = {
            "title": title,
            "source": "rottentomatoes",
            "rating": rating,
            "votes": votes,
            "genre": [],
            "timestamp": datetime.now().isoformat()
        }

        filmes.append(registo)
        vistos.add(title)

        if len(filmes) >= 10:
            break

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(filmes, f, ensure_ascii=False, indent=4)

    logging.info(f"Foram recolhidos {len(filmes)} filmes")
    print("Filmes encontrados:", len(filmes))


if __name__ == "__main__":
    main()