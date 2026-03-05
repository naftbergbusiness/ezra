# EZRA — Project Context for Claude

## What is EZRA?

EZRA (Executive Zero-Risk Assistant) is a self-hosted, local-first AI assistant stack running on dedicated hardware. It is designed for personal executive use with a strong emphasis on data sovereignty, auditability, and deliberate action.

## Hardware

- **CPU:** Intel Core i7-13700K (16 cores / 24 threads)
- **RAM:** 64 GB
- All services run locally on this machine unless explicitly routed otherwise.

## Stack & Services

### Docker
All services are containerized and managed via Docker (and Docker Compose). Treat Docker as the deployment primitive — do not suggest bare-metal installs.

### Ollama
Local LLM inference engine. Used for fast, private model runs. Models are pulled and managed through Ollama's API. Ollama runs inside Docker and is accessible at `http://ollama:11434` within the Docker network.

### Open WebUI
Web-based chat interface connected to Ollama (and optionally the Claude API). Provides the primary conversational UI for EZRA.

### n8n
Workflow automation platform. Used to orchestrate multi-step tasks, integrate services, and trigger agents. Accessible locally and over Tailscale.

### Tailscale
Secure mesh VPN used for private remote access to EZRA services. All external access to the stack goes through Tailscale — do not expose services to the public internet directly.

### SQLite + RAG
- **SQLite** is the primary local database for structured data, logs, and state.
- **RAG (Retrieval-Augmented Generation)** provides long-term memory and knowledge retrieval. Documents are embedded and stored locally; queries are augmented with retrieved context before being sent to the LLM.

### Claude API
Used for advanced reasoning, agentic tasks, and capabilities beyond local model limits. The Claude API is the preferred AI backend for complex, multi-step, or high-stakes tasks. Use `claude-sonnet-4-6` or `claude-opus-4-6` for production tasks; `claude-haiku-4-5-20251001` for lightweight/fast tasks.

## Key Principles for Claude

1. **Zero-risk defaults** — Prefer reversible actions. Always confirm before destructive or irreversible operations.
2. **Local-first** — Prefer solutions that run on-device. Use the Claude API only when local inference is insufficient.
3. **Docker as the deployment layer** — All new services should be containerized. Provide Docker Compose snippets when adding services.
4. **Tailscale for networking** — Do not suggest opening firewall ports to the internet. Route external access through Tailscale.
5. **SQLite for persistence** — Use SQLite for structured local data unless a specific use case demands otherwise.
6. **Auditability** — Log actions and decisions where practical. EZRA should be able to explain what it did and why.

## Development Notes

- Platform: Windows 11 Pro (host), Linux containers via Docker
- Shell: bash (Git Bash / WSL-compatible)
- This repo lives at `C:\Projects\ezra`
- Prefer Unix paths in scripts and configs (Docker handles path translation)

## Model Reference

| Model ID | Use Case |
|----------|----------|
| `claude-opus-4-6` | Complex reasoning, high-stakes agentic tasks |
| `claude-sonnet-4-6` | Default production tasks |
| `claude-haiku-4-5-20251001` | Fast, lightweight tasks |
