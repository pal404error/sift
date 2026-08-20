import argparse

import uvicorn

from llm_search.api import get_engine


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

    args = parser.parse_args()

    if args.command == "serve":
        uvicorn.run("llm_search.api:app", host="127.0.0.1", port=8000, reload=True)
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
