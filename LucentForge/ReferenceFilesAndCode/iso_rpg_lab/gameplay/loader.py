import json, os

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _index_by_id(seq, kind):
    out = {}
    for x in seq:
        if "id" not in x:
            raise ValueError(f"{kind} entry missing 'id': {x}")
        out[x["id"]] = x
    return out

def load_all(data_dir="data"):
    # required files
    items    = load_json(os.path.join(data_dir, "items.json"))
    abilities= load_json(os.path.join(data_dir, "abilities.json"))
    enemies  = load_json(os.path.join(data_dir, "enemies.json"))

    # players.json may be array or {"players":[...]}
    try:
        players_raw = load_json(os.path.join(data_dir, "players.json"))
    except FileNotFoundError:
        raise FileNotFoundError("Missing data/players.json — create it (see example in our last message).")

    if isinstance(players_raw, dict) and "players" in players_raw:
        players_list = players_raw["players"]
    elif isinstance(players_raw, list):
        players_list = players_raw
    else:
        raise ValueError("players.json must be a list of players or an object with a 'players' array.")

    return {
        "items":     _index_by_id(items,    "items"),
        "abilities": _index_by_id(abilities,"abilities"),
        "enemies":   _index_by_id(enemies,  "enemies"),
        "players":   _index_by_id(players_list, "players"),
    }
