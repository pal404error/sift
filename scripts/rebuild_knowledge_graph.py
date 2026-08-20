#!/usr/bin/env python3
"""Rebuild memory/knowledge-graph.json by scanning the codebase.

Walks the repo, extracts modules/classes/functions/routes and import/call edges for
Python and TypeScript, and writes a machine-readable graph. Run after every code change
(pre-commit hook or CI step).

Usage:  python3 scripts/rebuild_knowledge_graph.py
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "memory" / "knowledge-graph.json"
IGNORE_DIRS = {".git", "node_modules", ".scrape", "__pycache__", "dist", "build", ".venv", "venv"}

nodes: dict[str, dict] = {}
edges: list[dict] = []


def add_node(id_: str, type_: str, label: str, meta: dict | None = None):
    if id_ not in nodes:
        nodes[id_] = {"id": id_, "type": type_, "label": label, "meta": meta or {}}


def add_edge(src: str, dst: str, kind: str):
    edges.append({"source": src, "target": dst, "kind": kind})


def py_analysis(path: Path, rel: str):
    src = path.read_text(encoding="utf-8", errors="ignore")
    mod = rel.replace("/", ".").removesuffix(".py")
    add_node(f"mod:{mod}", "module", mod)
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            cid = f"{mod}.{node.name}"
            add_node(cid, "class", node.name, {"module": mod})
            add_edge(f"mod:{mod}", cid, "defines")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fid = f"{mod}.{node.name}"
            add_node(fid, "function", node.name, {"module": mod})
            add_edge(f"mod:{mod}", fid, "defines")
            # route detection (FastAPI/Flask)
            for dec in node.decorator_list:
                dec_src = ast.unparse(dec)
                m = re.search(r'\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)', dec_src)
                if m:
                    rid = f"route:{m.group(2)}:{node.name}"
                    add_node(rid, "route", f"{m.group(1).upper()} {m.group(2)}", {"handler": fid})
                    add_edge(fid, rid, "handles")
    # imports
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                add_edge(f"mod:{mod}", f"ext:{a.name}", "imports")
        elif isinstance(n, ast.ImportFrom) and n.module:
            add_edge(f"mod:{mod}", f"ext:{n.module}", "imports")


TS_IMPORT = re.compile(r'import\s+(?:[^;]*?\s+from\s+)?["\']([^"\']+)["\']')


def ts_analysis(path: Path, rel: str):
    src = path.read_text(encoding="utf-8", errors="ignore")
    mod = rel
    add_node(f"mod:{mod}", "module", rel)
    for m in TS_IMPORT.finditer(src):
        add_edge(f"mod:{mod}", f"ext:{m.group(1)}", "imports")
    for fn in re.finditer(r"(?:function|const)\s+([A-Za-z0-9_]+)\s*(?:=|\()", src):
        fid = f"{mod}.{fn.group(1)}"
        add_node(fid, "function", fn.group(1), {"module": mod})
        add_edge(f"mod:{mod}", fid, "defines")


def main():
    for p in ROOT.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix == ".py":
            py_analysis(p, str(p.relative_to(ROOT)))
        elif p.is_file() and p.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            ts_analysis(p, str(p.relative_to(ROOT)))
    add_node(
        "repo:LLM-search",
        "module",
        "LLM-search project root",
        {"language": "python+typescript", "status": "active"},
    )
    graph = {
        "schema_version": "1.0",
        "project": "LLM-search",
        "generated_at": __import__("datetime").date.today().isoformat(),
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {"node_count": len(nodes), "edge_count": len(edges)},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(graph, indent=2))
    stats = graph["stats"]
    print(f"Wrote {OUT}: {stats['node_count']} nodes, {stats['edge_count']} edges")


if __name__ == "__main__":
    main()
