import requests
import json
from datetime import datetime

API_KEY = "15758038"

filmes = ["Inception", "Interstellar", "The Matrix", "Titanic", "Avatar"]

dados = []

for filme in filmes:
    url = f"http://www.omdbapi.com/?t={filme}&apikey={API_KEY}"
    r = requests.get(url)
    data = r.json()

    if data.get("Response") == "True":
        registo = {
            "title": data.get("Title"),
            "source": "omdb",
            "rating": float(data.get("imdbRating", 0)),
            "votes": int(data.get("imdbVotes", "0").replace(",", "")),
            "genre": data.get("Genre", "").split(", "),
            "timestamp": datetime.now().isoformat()
        }

        dados.append(registo)

with open("data/filmes.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, indent=4)