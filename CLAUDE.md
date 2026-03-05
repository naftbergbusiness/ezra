# EZRA — Claude Project Context
**Executive Zero-Risk Assistant** | Project Bible v1.1 | March 2026
Owner: Naftoli Scheinberg

---

## What Is EZRA?

EZRA is a personal AI assistant ecosystem — not a single app. It is a hub-and-spoke architecture where the home PC is the always-on hub and every other device is a spoke. The goal is a Jarvis-like experience that grows smarter over time: automating tasks, surfacing relevant information, and serving as an always-available thinking partner.

**Owner profile:**
- Highly analytical, non-coder — can read and understand code
- Devices: Home PC (Windows), Work PC, Android phone, Chrome browser
- Ecosystem: Google Workspace (Gmail, Calendar, Sheets), WhatsApp
- Pain point: Information overload across too many sources
- Revenue goals: E-commerce automation, content monetization

---

## Hardware

| Component | Spec | EZRA Relevance |
|-----------|------|----------------|
| CPU | Intel Core i7-13700K | Excellent for CPU-based local AI |
| GPU | AMD Radeon RX 6700 XT | Limited AI use (AMD, not NVIDIA). Vulkan backend possible |
| RAM | 64 GB | Can run 8B models with massive headroom |
| Role | EZRA Central Server | Runs 24/7, hosts all core services |

**Future GPU upgrade:** When EZRA generates revenue, first hardware investment = used NVIDIA RTX 3090 (~$800). Unlocks GPU-accelerated inference and larger models.

---

## System Architecture

```
Gmail / Calendar / Sheets / WhatsApp
        |
        v
   n8n (Workflow Engine — the plumbing)
        |
   +----+----+
   v         v
Qwen3-8B    Claude API
(Fast triage) (Heavy thinking)
   |              |
   +------+-------+
          v
   SQLite + RAG (Memory & Context)
          |
          v
   Open WebUI (Chat interface)
          |
   Tailscale (Encrypted mesh to all devices)
          |
   Android / Work PC / Browser
          +
   Cowork (On-demand agentic tasks on local files)
```

---

## Four-Tier Intelligence Model

| Tier | Tool | Role | Example Tasks |
|------|------|------|---------------|
| Plumbing | n8n | Connects services, routes data. **Does not think.** | Pull emails every 5 min, check calendar, trigger workflows |
| Fast Triage | Qwen3-8B (local) | Quick classification, simple responses. Free, instant, always-on. | Is this email urgent? Categorize this. Is my calendar free Thursday? |
| Heavy Thinking | Claude API | Complex reasoning, nuanced analysis. Costs per use. | Summarize my morning, draft a client reply, analyze product data |
| Agentic Execution | Claude Cowork | Multi-step tasks on local files. Included in Pro. | Reorganize a folder, build a report from notes, create a presentation |

**Critical distinction:** n8n is the plumbing, not the brain. It connects and routes data. AI models do the actual thinking.

---

## Stack & Services

| Component | Tool | Cost | Purpose |
|-----------|------|------|---------|
| Local AI | Ollama + Qwen3-8B | Free | Fast triage, always-on responses |
| Heavy AI | Claude API | ~$15–40/mo | Complex reasoning, important decisions |
| Agentic Work | Claude Cowork | $0 (Pro) | Multi-step file tasks, document creation |
| Build Tool | Claude Code | $20/mo (Pro) | Writes, tests, debugs all EZRA code |
| Workflows | n8n (Docker) | Free | Connects services, routes data, triggers automations |
| Memory | SQLite + RAG | Free | Stores everything EZRA learns about you |
| Device Mesh | Tailscale | Free (≤3 devices) | Encrypted connections between all devices |
| Voice Input | Whisper (local) | Free | Speech-to-text for voice commands |
| Chat Interface | Open WebUI | Free | Private ChatGPT-like interface |
| Version Control | GitHub | Free | Stores all EZRA code, enables remote updates |

### Docker
Foundation of everything. Every service runs in Docker. Portable: copy config + data to new hardware and everything works identically.

### Ollama + Qwen3-8B
- Runs local LLM inference. Accessible at `http://ollama:11434` within Docker network.
- **Why Qwen3-8B:** Top-performing open-source 8B model. Unique dual-mode: thinking mode for complex reasoning, non-thinking mode for fast responses. Ideal for always-on use on CPU.
- Model is a replaceable component — swap via one Ollama command.
- Alternatives: Llama 4 8B, DeepSeek R1 7B, Gemma 3.

### Open WebUI
Primary chat interface. Connects to Ollama and Claude API. Accessible from any device via Tailscale.

### n8n
Visual workflow automation. The nervous system connecting EZRA to Gmail, Calendar, and external services. Workflows export as JSON — zero lock-in. Uses SQLite for its own DB.

### Tailscale
Encrypted mesh VPN. Home PC, Work PC, and Android phone on the same private network regardless of physical location. **No ports open to the public internet. All remote access via Tailscale.**
- Tailscale Serve URLs: `https://ezra.tail5c85c0.ts.net/` (Open WebUI), `https://ezra.tail5c85c0.ts.net/n8n` (n8n)

### SQLite + RAG (Memory System)
- **SQLite:** Single-file database. Zero config. Stores preferences, conversation history, task history, contacts.
- **RAG:** Before answering any question, EZRA searches its memory for relevant context and includes it in the prompt. Makes EZRA feel like it actually knows you.
- Chosen over Supabase deliberately — simpler, no extra services, upgradeable later if needed.

### Claude API
Used for complex reasoning and analysis. Called when real intelligence is needed. Separate billing from Claude Pro.
- Default: `claude-sonnet-4-6`
- Complex/high-stakes: `claude-opus-4-6`
- Fast/lightweight: `claude-haiku-4-5-20251001`

### Claude Cowork vs. EZRA

| Capability | Cowork | EZRA |
|------------|--------|------|
| Availability | Only while Desktop app is open | Always-on, 24/7 |
| Device access | Single machine | All devices via Tailscale |
| Persistent memory | No | SQLite + RAG |
| Background monitoring | No | Yes (n8n) |
| Complex file tasks | Excellent | Limited (8B model) |
| Scheduled automations | Basic | Full workflow engine (n8n) |

Use Cowork for on-demand frontier AI work on local files. Use EZRA for always-on infrastructure, cross-device access, and automated workflows. They are layers, not competitors.

---

## Security Golden Rules

| Rule | Meaning |
|------|---------|
| No autonomous spending | EZRA never buys, sells, or transfers money without explicit approval |
| No autonomous sending | EZRA drafts messages but never sends without confirmation |
| Encrypted at rest | All EZRA data on home PC is encrypted |
| Tailscale only | No ports open to public internet. All remote access via Tailscale |
| API key isolation | Each service gets its own API key with minimum permissions |
| Audit logging | EZRA logs every action it takes with timestamps |

**Conversation recording:** Do not implement always-on listening until legal requirements are reviewed (NJ is one-party consent, but employer policies and federal wiretapping laws also apply). Start with push-to-talk only.

---

## Phased Build Roadmap

| Phase | What | Timeline |
|-------|------|----------|
| 1 | Foundation (Docker, Ollama, Open WebUI, GitHub) | Day 1–2 ✅ |
| 2 | Get comfortable — daily use, learn model strengths/limits | Days 3–7 |
| 3 | Connect your life — n8n, Gmail, Calendar, Morning Briefing | Week 2 |
| 4 | Memory system — SQLite DB + RAG pipeline | Week 3–4 |
| 5 | Content agent — research, write, publish pipeline | Week 4–5 |
| 6 | E-commerce research — product research, listing writer | Week 4–5 |
| 7 | Voice interface — Whisper push-to-talk | Week 6+ |
| 8 | Advanced automation — cross-device, WhatsApp, proactive alerts | Week 8+ |

**Rule:** Speed up the building, but do not speed up the learning. Live with each feature before adding the next.

---

## Monthly Cost Baseline

| Item | Cost |
|------|------|
| Claude Pro (chat + Claude Code) | $20/mo |
| Claude API | $15–40/mo |
| Home PC electricity (24/7) | ~$10–20/mo |
| Tailscale, n8n, Ollama, Open WebUI, GitHub | $0 |
| **Total** | **$45–80/mo** |

---

## Development Workflow

1. Identify what to build or fix
2. Open Claude Code in terminal (`cd C:\Projects\ezra && claude`)
3. Describe what you want in plain English
4. Claude Code writes code, tests it, commits to GitHub
5. Review and approve — change is live

**Remote work:** Access home PC via Tailscale from Work PC or use Claude.ai in browser to draft changes.

---

## Current State

- Docker Compose stack running: Ollama, Open WebUI, n8n, Tailscale
- Local model: **Qwen3-8B** (5.2GB, CPU inference)
- Open WebUI admin: naftbergbusiness@gmail.com
- Tailscale node: `ezra.tail5c85c0.ts.net`
- Tailscale Serve: Open WebUI at `/`, n8n at `/n8n`
- Next phase: Connect Gmail + Google Calendar to n8n, build Morning Briefing workflow

---

## Instructions for Claude

- Always reference the four-tier model when designing features. n8n routes, Qwen3 triages, Claude API reasons, Cowork executes files.
- Default to simple solutions: SQLite over Postgres, local over cloud, minimal over complex.
- Always provide Claude Code commands when suggesting implementations.
- Enforce security rules — never suggest autonomous sending or spending.
- Naftoli is non-coder but highly analytical. Explain the why, not just the how. Skip boilerplate beginner explanations.
- When adding services, containerize them in Docker Compose.
- All external access routes through Tailscale. Never suggest opening firewall ports.
