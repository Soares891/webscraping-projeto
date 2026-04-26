import os
import json
import logging
from datetime import datetime

import requests
import feedparser
from bs4 import BeautifulSoup


RSS_URL = "https://www.rtp.pt/noticias/rss"
DATA_FILE = "data/noticias.json"
LOG_FILE = "logs/scraper.log"


os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def guardar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def extrair_texto(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        paragrafos = soup.find_all("p")
        return " ".join(p.get_text() for p in paragrafos)
    except:
        return ""


def main():
    logging.info("Início do scraping")

    feed = feedparser.parse(RSS_URL)
    dados = []

    for noticia in feed.entries[:5]:  # só 5 para testar
        texto = extrair_texto(noticia.link)

        dados.append({
            "titulo": noticia.title,
            "url": noticia.link,
            "data": noticia.get("published", ""),
            "texto": texto,
            "recolhido_em": datetime.now().isoformat()
        })

    guardar_dados(dados)

    logging.info("Scraping terminado")


if __name__ == "__main__":
    main()