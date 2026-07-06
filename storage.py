"""
Stockage persistant simple basé sur des fichiers JSON.
Suffisant pour un usage mono-utilisateur (un seul propriétaire de canal).
"""
import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

QUEUE_FILE = DATA_DIR / "queue.json"
STATE_FILE = DATA_DIR / "state.json"

DEFAULT_STATE = {
    "paused": False,
    "last_posted_item": None,   # copie du dernier contenu publié (pour répétition variée)
    "style_index": 0,           # pour faire tourner les formulations
}


def _load(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_queue() -> list[dict]:
    return _load(QUEUE_FILE, [])


def save_queue(queue: list[dict]) -> None:
    _save(QUEUE_FILE, queue)


def add_to_queue(item: dict) -> None:
    queue = load_queue()
    item["added_at"] = datetime.now(timezone.utc).isoformat()
    queue.append(item)
    save_queue(queue)


def pop_next() -> dict | None:
    """Retire et retourne le plus ancien élément de la file (FIFO)."""
    queue = load_queue()
    if not queue:
        return None
    item = queue.pop(0)
    save_queue(queue)
    return item


def load_state() -> dict:
    state = _load(STATE_FILE, dict(DEFAULT_STATE))
    for key, value in DEFAULT_STATE.items():
        state.setdefault(key, value)
    return state


def save_state(state: dict) -> None:
    _save(STATE_FILE, state)


def set_paused(paused: bool) -> None:
    state = load_state()
    state["paused"] = paused
    save_state(state)


def set_last_posted(item: dict | None) -> None:
    state = load_state()
    state["last_posted_item"] = item
    save_state(state)


def next_style_index(total_styles: int) -> int:
    """Fait tourner l'index de style à chaque appel, et le sauvegarde."""
    state = load_state()
    idx = state.get("style_index", 0)
    state["style_index"] = (idx + 1) % max(total_styles, 1)
    save_state(state)
    return idx
