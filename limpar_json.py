import json

DATA_FILE = "data/news.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    noticias = json.load(f)

noticias_limpas = []
urls_vistos = set()

for noticia in noticias:
    title = noticia.get("title", "")
    url = noticia.get("url", "")
    content = noticia.get("content", "")

    # Remove páginas de paginação
    if "/page/" in url:
        continue

    # Remove lixo do site
    if "Manage {vendor_count} vendors" in title:
        continue

    if "Manage {vendor_count} vendors" in content:
        continue

    if "All our premium content" in title:
        continue

    if "latest tech news delivered straight to your inbox" in content:
        continue

    # Remove duplicados por URL
    if url in urls_vistos:
        continue

    noticias_limpas.append(noticia)
    urls_vistos.add(url)

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(noticias_limpas, f, ensure_ascii=False, indent=4)

print("Antes:", len(noticias))
print("Depois:", len(noticias_limpas))
print("Removidas:", len(noticias) - len(noticias_limpas))