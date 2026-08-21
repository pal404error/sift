# Changelog

All notable changes to Sift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Early exploration for additional managed vector store integrations.

## [0.1.0] - 2026-08-21

### Added
- **Initial professional release!** 🚀
- **Pluggable Architecture**: Core framework supporting interchangeable LLM and embedding providers.
- **Vector Store Integration**: Robust, generic interfaces for vector storage and retrieval.
- **Crawl Orchestrator**: Built-in scheduling and management for data ingestion pipelines.
- **FastAPI Backend**: High-performance API endpoints for search, ingestion, and administration.
- **CLI (`sift`)**: Powerful developer command-line interface for local management.
- **Web UI**: Static, mobile-responsive frontend for immediate, out-of-the-box search.
- **Offline Evaluation**: Tooling to measure and track retrieval accuracy and generation quality.
- **Enterprise Auth**: OIDC/SSO support integrated directly into the core routing layer.
- **Observability**: Health checks and metrics endpoints ready for Prometheus/Grafana.
- Comprehensive setup scripts, Docker Compose configurations, and `.env` templating.
