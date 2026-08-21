# Sift

> The enterprise-ready, self-hostable RAG search engine that brings your data to life.

![CI](https://img.shields.io/github/actions/workflow/status/pal404error/sift/ci.yml?label=ci)
![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![OIDC](https://img.shields.io/badge/OIDC-supported-blue)

## Why Sift?

Building a reliable, production-ready RAG (Retrieval-Augmented Generation) system shouldn't mean wrestling with a dozen fragmented tools or giving up control over your data. We built Sift because we wanted a search engine that feels like magic to users, but gives developers total control behind the scenes. 

Whether you're standing up an internal knowledge base, adding semantic search to your product, or building an enterprise portal, Sift gives you a clean, pluggable foundation. It's built for scale, deeply customizable, and designed to run wherever you need it to run.

## Features at a Glance

- **Pluggable Architecture**: Bring your own LLMs and embedding models (OpenAI, Anthropic, local models, or write your own provider).
- **Batteries Included**: Vector store integration, crawling orchestration, and offline evaluation are built right in.
- **Enterprise Ready**: First-class support for OIDC authentication, SSO, and health metrics.
- **Developer First**: Comprehensive CLI (`sift`), FastAPI endpoints, and a static web UI to hit the ground running.
- **Self-Hostable**: Simple Docker Compose setup or bare-metal deployment. You own your data.

## ⚡ 30-Second Quickstart

Get up and running locally in seconds. Sift comes with fake providers out of the box so you can test the waters without API keys.

```bash
# 1. Clone and install
git clone https://github.com/pal404error/sift.git
cd sift
pip install -e .

# 2. Set up your environment (or just use the defaults!)
cp .env.example .env

# 3. Start the server
sift serve
```
*Prefer Docker? Just run `docker compose up -d` and you're good to go.*

## How it Works

Sift acts as the intelligent orchestration layer between your data sources and your users. 
1. **Ingest & Crawl**: The built-in crawl orchestrator pulls data from your sources.
2. **Embed & Store**: Text is chunked, passed through your chosen embedding provider, and stored in the vector database.
3. **Retrieve & Generate**: User queries are vectorized to retrieve relevant context, which is then fed into the LLM to generate accurate, source-backed answers.

## What You Get

- **API Endpoints**: Clean, documented FastAPI routes for search, ingestion, and admin tasks.
- **CLI (`sift`)**: Powerful command-line tools to manage indexes, trigger crawls, and evaluate performance.
- **Web UI**: A static, customizable HTML interface to search your data right out of the box.
- **Offline Eval**: Built-in tooling to measure retrieval accuracy and generation quality over time.
- **Crawl Orchestrator**: Schedule and manage data ingestion pipelines effortlessly.
- **Auth & Security**: Ready for enterprise deployment with SSO/OIDC integration.

## Configuration

Sift is highly configurable via environment variables. Check out `.env.example` in the repository root for a complete list of options for connecting to different LLMs, vector stores, and setting up authentication.

## Monitoring

Sift exposes Prometheus-style metrics at `GET /metrics` and standardized health probes at `GET /health/live` and `GET /health/ready`. To spin up a full observability stack locally:

```bash
docker compose --profile monitoring up -d
```

- **Prometheus** → http://localhost:9090 (scrapes `sift` at `/metrics` every 15s)
- **Grafana** → http://localhost:3000 (default login `admin`/`admin`; Prometheus pre-provisioned as a datasource)

Bring it down with `docker compose --profile monitoring down`.

## Get Involved

We love contributions! Whether it's a bug fix, a new provider integration, or a documentation improvement.

- Read our [Contributing Guide](CONTRIBUTING.md) to get started.
- Check out the full documentation in the [`docs/`](docs/) directory.
- Review our [Security Policy](SECURITY.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

---
*Built with ❤️ for developers who love clean architecture and great search.*
