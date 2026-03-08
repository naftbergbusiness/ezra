"""
EZRA Memory API
---------------
Provides persistent memory for EZRA via:
  - SQLite: structured storage (preferences, contacts, task log, conversation log)
  - ChromaDB: vector store for semantic search (RAG)
  - Ollama: embeddings via nomic-embed-text
"""

import sqlite3
import httpx
import chromadb
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# ── Config ─────────────────────────────────────────────────────────────────
OLLAMA_URL = "http://ollama:11434"
EMBED_MODEL = "nomic-embed-text"
DB_PATH = "/data/ezra.db"
CHROMA_PATH = "/data/chroma"

# ── Lifespan ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="EZRA Memory API", lifespan=lifespan)

# ── SQLite ──────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS preferences (
            key     TEXT PRIMARY KEY,
            value   TEXT NOT NULL,
            updated TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS contacts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            email   TEXT,
            phone   TEXT,
            notes   TEXT,
            updated TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS task_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source      TEXT NOT NULL,
            action      TEXT NOT NULL,
            summary     TEXT,
            status      TEXT DEFAULT 'completed',
            created     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS conversation_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            source      TEXT,
            created     TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

# ── Embeddings ──────────────────────────────────────────────────────────────
async def embed(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{OLLAMA_URL}/api/embeddings", json={
            "model": EMBED_MODEL,
            "prompt": text
        })
        r.raise_for_status()
        return r.json()["embedding"]

def get_chroma():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection("ezra_memory")

# ── Models ───────────────────────────────────────────────────────────────────
class MemoryStore(BaseModel):
    text: str
    metadata: Optional[dict] = {}

class MemorySearch(BaseModel):
    query: str
    n_results: int = 5

class Preference(BaseModel):
    key: str
    value: str

class Contact(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class TaskLog(BaseModel):
    source: str
    action: str
    summary: Optional[str] = None
    status: str = "completed"

class ConversationEntry(BaseModel):
    role: str
    content: str
    source: Optional[str] = None

# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "ezra-memory"}

# Memory (RAG)

@app.post("/memory/store")
async def memory_store(item: MemoryStore):
    """Embed and store a piece of text in the vector store."""
    vector = await embed(item.text)
    collection = get_chroma()
    doc_id = f"mem-{datetime.now(timezone.utc).timestamp()}"
    collection.add(
        ids=[doc_id],
        embeddings=[vector],
        documents=[item.text],
        metadatas=[{**item.metadata, "created": datetime.now(timezone.utc).isoformat()}]
    )
    return {"id": doc_id, "status": "stored"}

@app.post("/memory/search")
async def memory_search(item: MemorySearch):
    """Semantic search over stored memories."""
    vector = await embed(item.query)
    collection = get_chroma()
    results = collection.query(
        query_embeddings=[vector],
        n_results=item.n_results
    )
    return {
        "results": [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    }

# Preferences

@app.post("/preferences")
def set_preference(pref: Preference):
    conn = get_db()
    conn.execute(
        "INSERT INTO preferences (key, value, updated) VALUES (?, ?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated=excluded.updated",
        (pref.key, pref.value, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    return {"status": "saved", "key": pref.key}

@app.get("/preferences")
def get_preferences():
    conn = get_db()
    rows = conn.execute("SELECT * FROM preferences ORDER BY key").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/preferences/{key}")
def get_preference(key: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM preferences WHERE key=?", (key,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Preference not found")
    return dict(row)

# Contacts

@app.post("/contacts")
def add_contact(contact: Contact):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO contacts (name, email, phone, notes, updated) VALUES (?,?,?,?,?)",
        (contact.name, contact.email, contact.phone, contact.notes,
         datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    contact_id = cur.lastrowid
    conn.close()
    return {"status": "saved", "id": contact_id}

@app.get("/contacts")
def get_contacts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM contacts ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Task Log

@app.post("/tasks")
def log_task(task: TaskLog):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO task_log (source, action, summary, status, created) VALUES (?,?,?,?,?)",
        (task.source, task.action, task.summary, task.status,
         datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    return {"status": "logged", "id": task_id}

@app.get("/tasks")
def get_tasks(limit: int = 50):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM task_log ORDER BY created DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Conversation Log

@app.post("/conversations")
def log_conversation(entry: ConversationEntry):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO conversation_log (role, content, source, created) VALUES (?,?,?,?)",
        (entry.role, entry.content, entry.source,
         datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    entry_id = cur.lastrowid
    conn.close()
    return {"status": "logged", "id": entry_id}

@app.get("/conversations")
def get_conversations(limit: int = 50):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM conversation_log ORDER BY created DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
