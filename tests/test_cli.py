import sys
from unittest.mock import patch

from fastapi.testclient import TestClient

from llm_search.api import app
from llm_search.cli import main


def test_cli_serve():
    with patch("uvicorn.run") as mock_run:
        with patch.object(sys, "argv", ["sift", "serve"]):
            main()
            mock_run.assert_called_once_with(
                "llm_search.api:app", host="127.0.0.1", port=8000, reload=True
            )


def test_cli_ingest():
    with patch("llm_search.cli.get_engine") as mock_engine:
        with patch.object(sys, "argv", ["sift", "ingest", "http://example.com"]):
            main()
            mock_engine.return_value.ingest_url.assert_called_with("http://example.com")


def test_cli_crawl():
    with patch("llm_search.cli.get_engine") as mock_engine:
        argv = ["sift", "crawl", "http://example.com", "--max-pages", "10"]
        with patch.object(sys, "argv", argv):
            main()
            mock_engine.return_value.crawl_site.assert_called_with(
                "http://example.com", max_pages=10
            )


def test_cli_search(capsys):
    with patch("llm_search.cli.get_engine") as mock_engine:
        with patch.object(sys, "argv", ["sift", "search", "query"]):
            mock_engine.return_value.search.return_value = [
                {"payload": {"doc_url": "url", "doc_title": "title", "text": "text"}}
            ]
            main()
            mock_engine.return_value.search.assert_called_with("query")
            out, _ = capsys.readouterr()
            assert "url" in out
            assert "title" in out
            assert "text" in out


def test_cli_ask(capsys):
    with patch("llm_search.cli.get_engine") as mock_engine:
        with patch.object(sys, "argv", ["sift", "ask", "query"]):
            mock_engine.return_value.ask.return_value = {"answer": "answer", "sources": ["url"]}
            main()
            mock_engine.return_value.ask.assert_called_with("query")
            out, _ = capsys.readouterr()
            assert "answer" in out
            assert "url" in out


def test_index_html():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Sift Search" in response.text
