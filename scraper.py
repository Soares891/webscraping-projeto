import os
import re
import json
import time
import logging
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


FONTES = [
    {
        "name": "AI News - Latest",
        "domain": "artificialintelligence-news.com",
        "base_url": "https://www.artificialintelligence-news.com/news/",
        "page_pattern": "https://www.artificialintelligence-news.com/news/page/{page}/"
    },
    {
        "name": "AI News",
        "domain": "artificialintelligence-news.com",
        "base_url": "https://www.artificialintelligence-news.com/",
        "page_pattern": "https://www.artificialintelligence-news.com/page/{page}/"
    },
    {
        "name": "AI News - Artificial Intelligence",
        "domain": "artificialintelligence-news.com",
        "base_url": "https://www.artificialintelligence-news.com/categories/artificial-intelligence/",
        "page_pattern": "https://www.artificialintelligence-news.com/categories/artificial-intelligence/page/{page}/"
    },
    {
        "name": "AI News - All Categories",
        "domain": "artificialintelligence-news.com",
        "base_url": "https://www.artificialintelligence-news.com/all-categories/",
        "page_pattern": "https://www.artificialintelligence-news.com/all-categories/page/{page}/"
    }
]

DATA_FILE = "data/news.json"
LOG_FILE = "logs/scraper.log"

MAX_NOTICIAS = 2000
MAX_PAGINAS_POR_FONTE = 80

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


def gerar_id(url):
    return hashlib.md5(url.encode()).hexdigest()


def extrair_detalhes(url):
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    texto_pagina = soup.get_text(" ", strip=True)

    paragraphs = soup.find_all("p")
    conteudos_validos = []

    for p in paragraphs:
        texto = limpar_texto(p.get_text(" ", strip=True))

        if len(texto) < 50:
            continue

        ignorar = [
            "AI News is part of",
            "TechForge",
            "View all posts by",
            "Want to learn more",
            "Join our Community",
            "Subscribe now",
            "The technical storage or access",
            "Preferences",
            "Statistics",
            "Marketing"
        ]

        if any(frase in texto for frase in ignorar):
            continue

        conteudos_validos.append(texto)

    content = limpar_texto(" ".join(conteudos_validos))[:2500]

    author = None
    author_link = soup.find("a", href=re.compile(r"/author/"))
    if author_link:
        author = limpar_texto(author_link.get_text(" ", strip=True))

    published_at = None
    date_match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
        texto_pagina
    )
    if date_match:
        published_at = date_match.group(0)

    return content, published_at, author


def extrair_links_da_pagina(url_pagina, domain):
    try:
        response = requests.get(url_pagina, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as erro:
        logging.warning(f"Erro ao aceder à página {url_pagina}: {erro}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for link in soup.find_all("a", href=True):
        title = limpar_texto(link.get_text(" ", strip=True))
        href = link.get("href")
        url = urljoin(url_pagina, href)

        parsed = urlparse(url)

        if domain not in parsed.netloc:
            continue

        if "/news/" not in parsed.path:
            continue

        if not title or len(title) < 20:
            continue

        links.append({
            "title": title,
            "url": url
        })

    return links


def carregar_existentes():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def main():
    logging.info("Início do scraping com múltiplas fontes e paginação")

    noticias = carregar_existentes()
    urls_vistos = {noticia["url"] for noticia in noticias if "url" in noticia}

    for fonte in FONTES:
        print(f"\nFonte: {fonte['name']}")

        for pagina in range(1, MAX_PAGINAS_POR_FONTE + 1):
            if pagina == 1:
                url_pagina = fonte["base_url"]
            else:
                url_pagina = fonte["page_pattern"].format(page=pagina)

            print(f"A recolher página {pagina}: {url_pagina}")

            links = extrair_links_da_pagina(url_pagina, fonte["domain"])

            if not links:
                print("Sem links nesta página. A passar à próxima fonte.")
                break

            for item in links:
                title = item["title"]
                url = item["url"]

                if url in urls_vistos:
                    continue

                try:
                    content, published_at, author = extrair_detalhes(url)

                    if len(content) < 100:
                        continue

                    registo = {
                        "id": gerar_id(url),
                        "title": title,
                        "content": content,
                        "source": {
                            "name": fonte["name"],
                            "domain": fonte["domain"]
                        },
                        "url": url,
                        "published_at": published_at,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                        "author": author
                    }

                    noticias.append(registo)
                    urls_vistos.add(url)

                    print(f"{len(noticias)} - {title}")

                    time.sleep(0.4)

                except Exception as erro:
                    logging.warning(f"Erro ao processar notícia {url}: {erro}")

                if len(noticias) >= MAX_NOTICIAS:
                    break

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(noticias, f, ensure_ascii=False, indent=4)

            if len(noticias) >= MAX_NOTICIAS:
                break

            time.sleep(1)

        if len(noticias) >= MAX_NOTICIAS:
            break

    logging.info(f"Foram recolhidas {len(noticias)} notícias")
    print("\nTotal de notícias:", len(noticias))


if __name__ == "__main__":
    main()