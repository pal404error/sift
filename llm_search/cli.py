import argparse
import os
from types import SimpleNamespace

import uvicorn

from llm_search.api import app, get_engine

# A small bundled corpus so `sift demo` returns real results on first load
# (no API keys, no crawling required). Uses local MiniLM embeddings +
# cross-encoder reranking when available.
DEMO_DOCS: list[dict] = [
    {"id": "rag", "text": (
        "Retrieval augmented generation connects a vector index with a language "
        "model so the model can answer questions using your private documents."
    )},
    {"id": "rerank", "text": (
        "A reranker reorders the top retrieved passages with a cross encoder to "
        "boost answer relevance."
    )},
    {"id": "crawl", "text": (
        "The crawler fetches web pages while obeying robots.txt and a per host "
        "rate limit so it ingests sites politely."
    )},
    {"id": "oidc", "text": (
        "OIDC lets users log in through an external identity system; it checks a "
        "JWT signature against a JWKS public key for enterprise access control."
    )},
    {"id": "rbac", "text": (
        "Role based access control assigns each API key a role such as admin or "
        "user, and the audit log records every request."
    )},
    {"id": "eval", "text": (
        "The offline evaluation harness tracks recall, precision, and mean "
        "reciprocal rank to measure retrieval quality."
    )},
    {"id": "incremental", "text": (
        "Incremental crawling uses entity tags and last modified headers to skip "
        "pages that have not changed since the last visit."
    )},
    {"id": "cli", "text": (
        "The command line tool can serve the API, ingest a URL, crawl a site, and "
        "run a search without writing code."
    )},
    {"id": "webui", "text": (
        "The hosted query console shows retrieved passages together with "
        "clickable source links, so a visitor needs no installed software."
    )},
    {"id": "monitoring", "text": (
        "When the service is healthy it returns a 200 on the live probe and a "
        "503 with no details on the ready probe."
    )},
]


def main() -> None:
    parser = argparse.ArgumentParser(prog="sift")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("serve", help="Run uvicorn server")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a single URL")
    ingest_parser.add_argument("url", help="URL to ingest")

    crawl_parser = subparsers.add_parser("crawl", help="Crawl and ingest a site")
    crawl_parser.add_argument("url", help="Starting URL to crawl")
    crawl_parser.add_argument("--max-pages", type=int, default=20, help="Maximum pages to crawl")

    search_parser = subparsers.add_parser("search", help="Search indexed content")
    search_parser.add_argument("query", help="Search query")

    ask_parser = subparsers.add_parser("ask", help="Ask a question about indexed content")
    ask_parser.add_argument("query", help="Question to ask")

    demo_parser = subparsers.add_parser("demo", help="Serve with a seeded demo corpus")
    demo_parser.add_argument("--host", default="127.0.0.1")
    demo_parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "serve":
        uvicorn.run("llm_search.api:app", host="127.0.0.1", port=8000, reload=True)
    elif args.command == "demo":
        # Settings are cached on first use, so apply providers before building.
        os.environ.setdefault("EMBEDDING_PROVIDER", "local")
        os.environ.setdefault("RERANKER", "cross-encoder")
        from llm_search.config import get_settings

        get_settings.cache_clear()
        engine = get_engine()
        for d in DEMO_DOCS:
            engine._index_doc(SimpleNamespace(url=d["id"], title=d["id"], text=d["text"]))
        print(f"Seeded {len(DEMO_DOCS)} demo documents at http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.command == "ingest":
        engine = get_engine()
        engine.ingest_url(args.url)
        print(f"Ingested: {args.url}")
    elif args.command == "crawl":
        engine = get_engine()
        stats = engine.crawl_site(args.url, max_pages=args.max_pages)
        print(f"Crawl stats: {stats}")
    elif args.command == "search":
        engine = get_engine()
        results = engine.search(args.query)
        for r in results:
            print(f"[{r['payload'].get('doc_url')}] {r['payload'].get('doc_title')}")
            print(f"{r['payload'].get('text')}\n")
    elif args.command == "ask":
        engine = get_engine()
        result = engine.ask(args.query)
        print(result["answer"])
        print("\nSources:")
        for s in result["sources"]:
            print(f" - {s}")


if __name__ == "__main__":
    main()
