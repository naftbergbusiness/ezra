# EZRA — Executive Zero-Risk Assistant

EZRA is a personal AI-powered executive assistant designed to operate with zero-risk principles — ensuring all actions are deliberate, auditable, and aligned with your goals.

## Overview

EZRA serves as a local-first intelligence layer that integrates automation, knowledge management, and AI-driven decision support into a unified, self-hosted stack. It runs entirely on your own hardware with no mandatory cloud dependencies, keeping sensitive data under your control.

## Core Capabilities

- **Workflow Automation** — Orchestrates tasks and pipelines via n8n
- **Knowledge & Memory** — Persistent context using SQLite + RAG (Retrieval-Augmented Generation)
- **AI Inference** — Local LLM execution via Ollama; cloud reasoning via Claude API
- **Web Interface** — Conversational UI through Open WebUI
- **Secure Networking** — Private, encrypted access via Tailscale
- **Containerized Deployment** — All services managed with Docker

## Philosophy

Zero-risk means every action EZRA takes is traceable, reversible where possible, and never executed without sufficient context. EZRA is built to augment executive judgment — not replace it.

## Stack

| Component | Role |
|-----------|------|
| Docker | Service orchestration & isolation |
| Ollama | Local LLM inference |
| Open WebUI | Chat interface |
| n8n | Workflow automation |
| Tailscale | Secure remote access |
| SQLite + RAG | Persistent memory & knowledge retrieval |
| Claude API | Advanced reasoning & agentic tasks |

## Getting Started

See `CLAUDE.md` for full project context and architecture notes.
