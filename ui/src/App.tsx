import React, { useState } from "react";
import * as ThreeUI from "@designcodeio/threeui";
import { askStream, search, type SearchHit } from "./api";
import { ThreeUIBoundary } from "./ThreeUIBoundary";

// ThreeUI components are typed loosely and pull in shader assets at runtime, so we
// treat them as untyped here and always render them behind a ThreeUIBoundary.
const Toggle = ThreeUI.SkeuomorphicToggle as any;
const Badge = ThreeUI.SparkBadge as any;
const Backdrop = (ThreeUI.TopoField ?? ThreeUI.StreamConvergenceBackground) as any;

export default function App() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"search" | "ask">("search");
  const [hyde, setHyde] = useState(false);
  const [loading, setLoading] = useState(false);
  const [answering, setAnswering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SearchHit[]>([]);
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);

  function onChangeHyde(v: unknown) {
    if (typeof v === "boolean") setHyde(v);
    else if (v && typeof v === "object" && "target" in v)
      setHyde(!!(v as { target: { checked: boolean } }).target.checked);
    else setHyde(!hyde);
  }

  async function runSearch() {
    setLoading(true);
    setError(null);
    setAnswer("");
    setSources([]);
    try {
      const hits = await search(query, { topK: 8, hyde });
      setResults(hits);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  async function runAsk() {
    setAnswering(true);
    setError(null);
    setResults([]);
    setAnswer("");
    setSources([]);
    try {
      await askStream(query, { hyde }, {
        onSources: setSources,
        onToken: (t) => setAnswer((a) => a + t),
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setAnswering(false);
    }
  }

  function submit() {
    if (!query.trim()) return;
    if (mode === "search") void runSearch();
    else void runAsk();
  }

  return (
    <div className="app">
      <ThreeUIBoundary fallback={<div className="backdrop-fallback" />}>
        <div className="backdrop">
          <Backdrop />
        </div>
      </ThreeUIBoundary>

      <main className="shell">
        <header className="brand">
          <div className="logo">Sift</div>
          <p className="tagline">
            Self-hostable multi-provider RAG search over web content.
          </p>
        </header>

        <section className="composer glass">
          <div className="mode-switch" role="tablist" aria-label="Mode">
            <button
              role="tab"
              aria-selected={mode === "search"}
              className={mode === "search" ? "active" : ""}
              onClick={() => setMode("search")}
            >
              Search
            </button>
            <button
              role="tab"
              aria-selected={mode === "ask"}
              className={mode === "ask" ? "active" : ""}
              onClick={() => setMode("ask")}
            >
              Ask
            </button>
          </div>

          <div className="search-row">
            <input
              className="query"
              type="text"
              value={query}
              placeholder={
                mode === "ask"
                  ? "Ask a question…"
                  : "Search the index…"
              }
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") submit();
              }}
              autoFocus
            />
            <button className="primary" onClick={submit} disabled={loading || answering}>
              {mode === "ask" ? (answering ? "Answering…" : "Ask") : loading ? "Searching…" : "Search"}
            </button>
          </div>

          <div className="controls">
            <ThreeUIBoundary
              fallback={
                <label className="hyde-fallback">
                  <input
                    type="checkbox"
                    checked={hyde}
                    onChange={(e) => setHyde(e.target.checked)}
                  />{" "}
                  HyDE
                </label>
              }
            >
              <div className="hyde-control">
                <Toggle checked={hyde} onChange={onChangeHyde} />
                <span>HyDE</span>
              </div>
            </ThreeUIBoundary>
          </div>
        </section>

        {error && <div className="error glass">{error}</div>}

        {mode === "search" && (
          <section className="results">
            {results.length === 0 && !loading && (
              <p className="empty">No results yet. Run a search to get started.</p>
            )}
            {results.map((r) => (
              <article className="card glass" key={r.id}>
                <div className="card-head">
                  <a
                    className="card-title"
                    href={r.payload.doc_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {r.payload.doc_title || r.payload.doc_url}
                  </a>
                  <ThreeUIBoundary
                    fallback={<span className="score-pill">{r.score.toFixed(3)}</span>}
                  >
                    <Badge label={r.score.toFixed(3)} />
                  </ThreeUIBoundary>
                </div>
                <p className="card-text">{r.payload.text}</p>
                <a
                  className="card-url"
                  href={r.payload.doc_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {r.payload.doc_url}
                </a>
              </article>
            ))}
          </section>
        )}

        {mode === "ask" && (
          <section className="answer">
            <article className="card glass">
              <h3 className="answer-head">Answer</h3>
              <div className="answer-body">
                {answer ? answer : answering ? "Thinking…" : "Ask a question to see a sourced answer."}
              </div>
              {sources.length > 0 && (
                <div className="sources">
                  <h4>Sources</h4>
                  <ul>
                    {sources.map((s, i) => (
                      <li key={`${s}-${i}`}>
                        <a href={s} target="_blank" rel="noreferrer">
                          {s}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          </section>
        )}

        <footer className="foot">
          Powered by Sift · vector + lexical retrieval · streaming answers
        </footer>
      </main>
    </div>
  );
}
