"""
EZRA Content Agent API
-----------------------
Manages EZRA's autonomous content strategy and generation pipeline.

Endpoints:
  Strategy  - store/retrieve niche + platform + format decisions
  Queue     - content pending approval
  Approval  - approve or reject queued content
  Research  - log research runs
  Published - content that has been approved and exported
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional

DB_PATH = "/data/content.db"
EXPORT_PATH = "/data/exports"

# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(EXPORT_PATH).mkdir(parents=True, exist_ok=True)
    init_db()
    yield

app = FastAPI(title="EZRA Content Agent", lifespan=lifespan)

# ── SQLite ────────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS strategies (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            niche           TEXT NOT NULL,
            platform        TEXT NOT NULL,
            content_format  TEXT NOT NULL,
            rationale       TEXT,
            monetization    TEXT,
            target_audience TEXT,
            posting_cadence TEXT,
            status          TEXT DEFAULT 'active',
            created         TEXT NOT NULL,
            updated         TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS content_queue (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id     INTEGER REFERENCES strategies(id),
            niche           TEXT NOT NULL,
            platform        TEXT NOT NULL,
            content_format  TEXT NOT NULL,
            title           TEXT NOT NULL,
            body            TEXT NOT NULL,
            hook            TEXT,
            cta             TEXT,
            tags            TEXT,
            status          TEXT DEFAULT 'pending',
            rejection_note  TEXT,
            created         TEXT NOT NULL,
            updated         TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS research_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            research_type   TEXT NOT NULL,
            summary         TEXT NOT NULL,
            raw_json        TEXT,
            created         TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS performance_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id      INTEGER REFERENCES content_queue(id),
            platform        TEXT,
            metric          TEXT,
            value           REAL,
            recorded        TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def now():
    return datetime.now(timezone.utc).isoformat()

# ── Models ────────────────────────────────────────────────────────────────────
class Strategy(BaseModel):
    niche: str
    platform: str
    content_format: str
    rationale: Optional[str] = None
    monetization: Optional[str] = None
    target_audience: Optional[str] = None
    posting_cadence: Optional[str] = None

class ContentItem(BaseModel):
    strategy_id: Optional[int] = None
    niche: str
    platform: str
    content_format: str
    title: str
    body: str
    hook: Optional[str] = None
    cta: Optional[str] = None
    tags: Optional[str] = None

class ApprovalAction(BaseModel):
    note: Optional[str] = None

class ResearchLog(BaseModel):
    research_type: str
    summary: str
    raw_json: Optional[str] = None

class PerformanceEntry(BaseModel):
    content_id: int
    platform: str
    metric: str
    value: float

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "ezra-content"}

# ── Strategies ────────────────────────────────────────────────────────────────
@app.post("/strategies")
def create_strategy(s: Strategy):
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO strategies
           (niche, platform, content_format, rationale, monetization,
            target_audience, posting_cadence, created, updated)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (s.niche, s.platform, s.content_format, s.rationale,
         s.monetization, s.target_audience, s.posting_cadence, now(), now())
    )
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return {"status": "created", "id": sid}

@app.get("/strategies")
def list_strategies(status: str = "active"):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM strategies WHERE status=? ORDER BY created DESC", (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.patch("/strategies/{sid}/pause")
def pause_strategy(sid: int):
    conn = get_db()
    conn.execute("UPDATE strategies SET status='paused', updated=? WHERE id=?", (now(), sid))
    conn.commit()
    conn.close()
    return {"status": "paused", "id": sid}

@app.patch("/strategies/{sid}/activate")
def activate_strategy(sid: int):
    conn = get_db()
    conn.execute("UPDATE strategies SET status='active', updated=? WHERE id=?", (now(), sid))
    conn.commit()
    conn.close()
    return {"status": "activated", "id": sid}

# ── Content Queue ─────────────────────────────────────────────────────────────
@app.post("/content/queue")
def enqueue_content(item: ContentItem):
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO content_queue
           (strategy_id, niche, platform, content_format, title, body,
            hook, cta, tags, created, updated)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (item.strategy_id, item.niche, item.platform, item.content_format,
         item.title, item.body, item.hook, item.cta, item.tags, now(), now())
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return {"status": "queued", "id": cid}

@app.get("/content/queue")
def get_queue(status: str = "pending"):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM content_queue WHERE status=? ORDER BY created DESC", (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/content/queue/{cid}")
def get_content_item(cid: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM content_queue WHERE id=?", (cid,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Content not found")
    return dict(row)

@app.post("/content/approve/{cid}")
def approve_content(cid: int, action: ApprovalAction = ApprovalAction()):
    conn = get_db()
    row = conn.execute("SELECT * FROM content_queue WHERE id=?", (cid,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Content not found")

    conn.execute(
        "UPDATE content_queue SET status='approved', updated=? WHERE id=?", (now(), cid)
    )
    conn.commit()

    # Export to markdown file
    item = dict(row)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"{EXPORT_PATH}/{ts}-{item['platform']}-{cid}.md"
    with open(filename, "w") as f:
        f.write(f"# {item['title']}\n\n")
        if item.get("hook"):
            f.write(f"**Hook:** {item['hook']}\n\n")
        f.write(f"{item['body']}\n\n")
        if item.get("cta"):
            f.write(f"**CTA:** {item['cta']}\n\n")
        if item.get("tags"):
            f.write(f"**Tags:** {item['tags']}\n\n")
        f.write(f"---\n*Niche: {item['niche']} | Platform: {item['platform']} | Format: {item['content_format']}*\n")

    conn.close()
    return {"status": "approved", "id": cid, "exported_to": filename}

@app.post("/content/reject/{cid}")
def reject_content(cid: int, action: ApprovalAction = ApprovalAction()):
    conn = get_db()
    conn.execute(
        "UPDATE content_queue SET status='rejected', rejection_note=?, updated=? WHERE id=?",
        (action.note, now(), cid)
    )
    conn.commit()
    conn.close()
    return {"status": "rejected", "id": cid}

@app.get("/content/export/{cid}", response_class=PlainTextResponse)
def export_content(cid: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM content_queue WHERE id=?", (cid,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Content not found")
    item = dict(row)
    md = f"# {item['title']}\n\n"
    if item.get("hook"):
        md += f"**Hook:** {item['hook']}\n\n"
    md += f"{item['body']}\n\n"
    if item.get("cta"):
        md += f"**CTA:** {item['cta']}\n\n"
    if item.get("tags"):
        md += f"**Tags:** {item['tags']}\n\n"
    return md

# ── Research Log ──────────────────────────────────────────────────────────────
@app.post("/research")
def log_research(entry: ResearchLog):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO research_log (research_type, summary, raw_json, created) VALUES (?,?,?,?)",
        (entry.research_type, entry.summary, entry.raw_json, now())
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return {"status": "logged", "id": rid}

@app.get("/research")
def get_research(limit: int = 20):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM research_log ORDER BY created DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Performance ───────────────────────────────────────────────────────────────
@app.post("/performance")
def log_performance(entry: PerformanceEntry):
    conn = get_db()
    conn.execute(
        "INSERT INTO performance_log (content_id, platform, metric, value, recorded) VALUES (?,?,?,?,?)",
        (entry.content_id, entry.platform, entry.metric, entry.value, now())
    )
    conn.commit()
    conn.close()
    return {"status": "logged"}

@app.get("/performance")
def get_performance():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM performance_log ORDER BY recorded DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.get("/dashboard")
def dashboard():
    conn = get_db()
    return {
        "strategies": {
            "active": conn.execute("SELECT COUNT(*) FROM strategies WHERE status='active'").fetchone()[0],
            "paused": conn.execute("SELECT COUNT(*) FROM strategies WHERE status='paused'").fetchone()[0],
        },
        "content": {
            "pending": conn.execute("SELECT COUNT(*) FROM content_queue WHERE status='pending'").fetchone()[0],
            "approved": conn.execute("SELECT COUNT(*) FROM content_queue WHERE status='approved'").fetchone()[0],
            "rejected": conn.execute("SELECT COUNT(*) FROM content_queue WHERE status='rejected'").fetchone()[0],
        },
        "research_runs": conn.execute("SELECT COUNT(*) FROM research_log").fetchone()[0],
    }
