import os
import re
import json
import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.artificialintelligence-news.com/"
DATA_FILE = "data/news.json"
LOG_FILE = "logs/scraper.log"

os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

headers = {
    "User-Agent": "Mozilla/5.0"
}


def limpar_texto(texto):
    return re.sub(r"\s+", " ", texto).strip()


def extrair_detalhes(url):
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    texto_pagina = soup.get_text(" ", strip=True)

    # Conteúdo da notícia
    paragraphs = soup.find_all("p")
    conteudos_validos = []

    for p in paragraphs:
        texto = limpar_texto(p.get_text(" ", strip=True))

        if len(texto) < 50:
            continue

        if "AI News is part of" in texto:
            continue

        if "TechForge" in texto:
            continue

        if "View all posts by" in texto:
            continue

        if "Want to learn more about AI" in texto:
            continue

        if "Check out" in texto and "event" in texto.lower():
            continue

        conteudos_validos.append(texto)

    content = limpar_texto(" ".join(conteudos_validos))[:2500]

    # Autor
    author = None
    author_link = soup.find("a", href=re.compile(r"/author/"))
    if author_link:
        author = limpar_texto(author_link.get_text(" ", strip=True))

    # Data
    published_at = None
    date_match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
        texto_pagina
    )
    if date_match:
        published_at = date_match.group(0)

    # Comentários
    comments = 0

    return content, published_at, author, comments


def main():
    logging.info("Início do scraping AI News")

    response = requests.get(BASE_URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    noticias = []
    urls_vistos = set()

    for link in soup.find_all("a", href=True):
        title = limpar_texto(link.get_text(" ", strip=True))
        href = link.get("href")
        url = urljoin(BASE_URL, href)

        if "artificialintelligence-news.com/news/" not in url:
            continue

        if not title or len(title) < 20:
            continue

        if url in urls_vistos:
            continue

        try:
            content, published_at, author, comments = extrair_detalhes(url)

            if len(content) < 100:
                continue

            registo = {
                "title": title,
                "content": content,
                "source": "AI News",
                "url": url,
                "published_at": published_at,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "author": author,
            }

            noticias.append(registo)
            urls_vistos.add(url)

        except Exception as erro:
            logging.warning(f"Erro ao processar notícia {url}: {erro}")

        if len(noticias) >= 10:
            break

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    logging.info(f"Foram recolhidas {len(noticias)} notícias")
    print("Notícias:", len(noticias))


if __name__ == "__main__":
    main()