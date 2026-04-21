import json
from urllib.parse import quote
from src.api_client import get_puuid, fetch_matches

if __name__ == "__main__":
    name = "little elephant"
    tag = "270"
    puuid = get_puuid(quote(name), tag)         # quote encode le texte au format URL
    matches_info = fetch_matches(puuid)

    with open("data/matches.json", "w") as f:   # Ecrit le json resultant dans un fichier
        json.dump(matches_info, f, indent=2)
