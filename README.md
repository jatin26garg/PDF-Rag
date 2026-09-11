# 🛡️ Sovereign AI Workbench

**A self-hosted, air-gapped AI workbench for defense, PSU, and government environments.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.9+-red.svg)](https://qdrant.tech/)
[![BGE-M3](https://img.shields.io/badge/BGE--M3-1.0-purple.svg)](https://huggingface.co/BAAI/bge-m3)
[![Qwen3](https://img.shields.io/badge/Qwen3--8B-1.0-orange.svg)](https://ollama.com/library/qwen3:8b)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [The Problem](#-the-problem)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [How It Works](#-how-it-works)
- [Workspace Layout](#-workspace-layout)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [SIH Alignment](#-sih-alignment)
- [License](#-license)

---

## 🎯 Overview

**Sovereign AI Workbench** is a fully local, air-gapped AI assistant that runs entirely on an
organization's own infrastructure. It provides a chat + agent interface over internal documents,
performs hybrid search, and coordinates tools to produce real deliverables — with **zero external
API calls**.

Built for environments where cloud AI assistants (ChatGPT, Claude, Codex) are prohibited due to
data sovereignty, this system gives industrial users a Claude/Codex-style workbench they can
actually use — without any data leaving the premises.

**Core capabilities:**

- 📄 **Document RAG** — Upload PDFs, DOCX, TXT; ask questions; get cited answers
- 🔍 **Hybrid Search** — Combines semantic + keyword retrieval via BGE-M3 + Qdrant
- 🤖 **Agent Orchestrator** — Plans and executes multi-step tasks using tools
- 📁 **File System Tool** — Sandboxed read/write within a workspace
- 🔒 **Zero External Calls** — Verified via network monitoring

---

## ❗ The Problem

Refineries, PSUs, defense-linked manufacturing, and government offices generate enormous volumes
of sensitive knowledge work — approval notes, board presentations, engineering calculations,
internal code, scanned drawings, inspection reports. None of this can go through cloud AI because
the underlying data is confidential (P&IDs, financials, vendor negotiations, unreleased designs).

Company policy keeps this data on-premises, so today people either:

1. Do the work **manually** → lost productivity, or
2. **Quietly paste** confidential material into public tools → data leakage

**Nothing deployable exists today** that industrial users can work with the way they use
Claude or Codex — until now.

---

## 🏗️ Architecture
