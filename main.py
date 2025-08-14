# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os

ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT, "data")

app = FastAPI(title="NLP-Hypnosis-Sales Toolkit API",
              description="Serve and manipulate NLP / Hypnosis / Sales content as JSON for apps and AI Studio.",
              version="1.0.0")

# ---------- Models ----------
class PackRequest(BaseModel):
    pack: str  # "nlp" | "hypnosis" | "sales"
    sections: Optional[List[str]] = None  # optional list of section keys to fetch
    format: Optional[str] = "json"  # future: "poster", "flashcard", etc.
    options: Optional[Dict[str,Any]] = None  # rendering options

class SearchRequest(BaseModel):
    q: str

# ---------- Helpers ----------
def load_pack(pack_name: str) -> Dict[str,Any]:
    fname = os.path.join(DATA_DIR, f"{pack_name.lower()}.json")
    if not os.path.exists(fname):
        raise FileNotFoundError(f"Pack not found: {pack_name}")
    with open(fname, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_sections(full_pack: Dict[str,Any], keys: Optional[List[str]]):
    if not keys:
        return full_pack
    filtered = {k: v for k,v in full_pack.items() if k in keys}
    return filtered

# ---------- Endpoints ----------
@app.get("/")
def health():
    return {"status":"ok", "service":"nlp-hypnosis-sales-toolkit", "version":"1.0.0"}

@app.get("/packs")
def list_packs():
    files = [f.split(".json")[0] for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    return {"available_packs": files}

@app.post("/get_pack")
def get_pack(req: PackRequest):
    pack_name = req.pack.lower()
    try:
        content = load_pack(pack_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_name}' not found.")
    filtered = filter_sections(content, req.sections)
    return {"pack": pack_name, "content": filtered, "meta": {"format": req.format, "options": req.options or {}}}

@app.post("/search")
def search_pack(req: SearchRequest, pack: Optional[str] = None):
    q = req.q.strip().lower()
    results = []
    packs = [pack] if pack else [f.split(".json")[0] for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    for p in packs:
        try:
            data = load_pack(p)
        except FileNotFoundError:
            continue
        for sec, text in data.items():
            if q in (sec.lower() + " " + text.lower()):
                results.append({"pack": p, "section": sec, "excerpt": text[:300]})
    return {"query": q, "results": results}

@app.post("/render_payload")
def render_payload(req: PackRequest):
    """
    Returns a single JSON payload that frontends or AI Studio can use
    to generate visuals, posters, or flashcards. Keeps everything decoupled.
    """
    try:
        content = load_pack(req.pack.lower())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Pack '{req.pack}' not found.")
    sections = filter_sections(content, req.sections)
    payload = {
        "pack": req.pack,
        "style": {
            "theme": req.pack.lower(),
            "palette": {
                "nlp": {"bg":"#ffffff","primary":"#0B5F9A","accent":"#2A9D7D"},
                "hypnosis": {"bg":"#e8f2ff","primary":"#4750B8","accent":"#2AA199"},
                "sales": {"bg":"#fff9e6","primary":"#D9534F","accent":"#E89E2D"}
            }.get(req.pack.lower(), {}),
            "fonts": ["Inter","Nunito"]
        },
        "sections": sections,
        "options": req.options or {}
    }
    return payload

# ---------- Admin / Utility ----------
@app.get("/schema")
def schema():
    """Return a small config / metadata file to help AI Studio editors."""
    cfg_path = os.path.join(ROOT, "app_schema", "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"error":"config.json missing"}

# ---------- Simple template preview (optional) ----------
@app.get("/preview/{pack_name}")
def preview(pack_name: str):
    try:
        content = load_pack(pack_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Pack not found")
    # return a minimal HTML preview (danger: not full design)
    html = "<html><head><meta charset='utf-8'><title>Preview</title></head><body>"
    html += f"<h1>{pack_name.title()} Preview</h1>"
    for k,v in content.items():
        html += f"<section><h2>{k}</h2><p>{v}</p></section>"
    html += "</body></html>"
    return html
