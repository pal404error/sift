import React, { useState } from "react";

const INSTALL = 'pip install "sift @ git+https://github.com/pal404error/sift.git"';

const FEATURES = [
  { icon: "P", title: "Pluggable Providers", body: "Swap LLMs and embeddings via config. First-class OpenAI, Anthropic, Ollama support, plus fakes for local testing." },
  { icon: "V", title: "Flexible Storage", body: "Store your vector embeddings in-memory for quick iteration, or scale seamlessly with built-in Qdrant vector store integration." },
  { icon: "S", title: "Enterprise Security", body: "Deploy confidently with OIDC/JWKS authentication, API-key Role Based Access Control (RBAC), and a comprehensive audit log." },
  { icon: "R", title: "Advanced Retrieval", body: "Achieve higher precision by combining lexical search with cross-encoder rerankers for top-tier semantic accuracy." },
  { icon: "C", title: "Concurrent Crawler", body: "Built-in crawl orchestrator fully respects robots.txt, supports ETags, and enables incremental updates to keep your index fresh." },
  { icon: "O", title: "Ops & Monitoring", body: "Ships with a powerful CLI, static web UI, offline eval harness, /metrics and /health probes for Prometheus + Grafana." },
];

const STEPS = [
  { n: "1", title: "Ingest & Crawl", body: "The orchestrator concurrently pulls pages from your sources, respecting robots.txt and gracefully handling incremental re-crawls via ETags." },
  { n: "2", title: "Embed & Store", body: "Content is intelligently chunked, passed through your chosen embedding provider, and indexed into your active vector store." },
  { n: "3", title: "Retrieve & Generate", body: "Queries are vectorized, optionally reranked with cross-encoders, and answered by your preferred LLM with transparent sources attached." },
];

const FAQ = [
  { q: "Is Sift Fully Open Source?", a: "Yes, Sift is completely open source and released under the permissive MIT license. You can fork it, modify it, and use it freely for both personal and commercial enterprise projects." },
  { q: "Which AI Models Does Sift Support?", a: "Sift features a highly pluggable architecture. Out of the box, we provide first-class support for OpenAI, Anthropic, and Ollama (for local inference). We also include mock fake providers that let you test the entire pipeline without requiring API keys or internet access." },
  { q: "How Does The Crawl Orchestrator Work?", a: "The built-in concurrent crawler orchestrator is designed for production efficiency. It strictly obeys robots.txt, supports ETags for bandwidth-saving incremental crawls, and handles chunking securely before passing data to the embedding pipeline." },
  { q: "Can I Integrate This With My Existing Identity Provider?", a: "Absolutely. Sift includes enterprise-ready OIDC and JWKS authentication, alongside API-key based Role Based Access Control (RBAC). It's built to drop straight into corporate environments securely." },
  { q: "How Do I Monitor Sift In Production?", a: "Sift comes instrumented with /metrics and /health endpoints natively. It seamlessly integrates with Prometheus and Grafana for comprehensive observability, and maintains a robust audit log for security tracing." },
];

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  function copyInstall() {
    navigator.clipboard?.writeText(INSTALL).then(() => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="page">
      <div className="backdrop" aria-hidden="true">
        <span className="aurora a" />
        <span className="aurora b" />
        <span className="aurora c" />
      </div>

      <header className="nav glass">
        <a className="brand" href="#home">Sift</a>
        <nav className={menuOpen ? "nav-links open" : "nav-links"}>
          <a href="#features" onClick={() => setMenuOpen(false)}>Features</a>
          <a href="#how" onClick={() => setMenuOpen(false)}>How It Works</a>
          <a href="#quickstart" onClick={() => setMenuOpen(false)}>Quickstart</a>
          <a href="#faq" onClick={() => setMenuOpen(false)}>FAQ</a>
          <a href="https://github.com/pal404error/sift#readme" onClick={() => setMenuOpen(false)}>Docs</a>
        </nav>
        <a href="https://github.com/pal404error/sift" className="gh-btn">GitHub</a>
        <button className="menu-toggle" onClick={() => setMenuOpen((v) => !v)} aria-label="Menu">Menu</button>
      </header>

      <main>
        <section className="hero" id="home">
          <span className="kicker">Enterprise, Self-Hostable RAG</span>
          <h1>Intelligence,<br />Grounded.</h1>
          <p className="deck">
            The enterprise-ready, self-hostable multi-provider RAG search engine.
            Bring your own models, keep your own data, and answer with source-backed retrieval.
          </p>
          <div className="hero-actions">
            <a href="#quickstart" className="btn primary">Get Started</a>
            <a href="https://github.com/pal404error/sift" className="btn ghost">GitHub Repository</a>
          </div>
          <div className="install glass">
            <code>{INSTALL}</code>
            <button onClick={copyInstall}>{copied ? "Copied!" : "Copy"}</button>
          </div>
        </section>

        <section className="section" id="features">
          <div className="section-head">
            <span className="kicker">Capabilities</span>
            <h2>Everything You Need To Ship Search</h2>
            <p>A clean, pluggable foundation — not a walled garden. Wire in your stack and stay in control.</p>
          </div>
          <div className="grid">
            {FEATURES.map((f) => (
              <article className="card glass" key={f.title}>
                <div className="ficon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.body}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section" id="how">
          <div className="section-head">
            <span className="kicker">The Pipeline</span>
            <h2>How It Works</h2>
            <p>Three stages between your sources and a grounded answer.</p>
          </div>
          <div className="steps">
            {STEPS.map((s) => (
              <div className="step glass" key={s.n}>
                <div className="num">{s.n}</div>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="section" id="quickstart">
          <div className="section-head">
            <span className="kicker">Wire Dispatch</span>
            <h2>Up And Running In Seconds</h2>
            <p>Sift ships with mock providers natively, letting you test the full RAG pipeline offline with zero API keys.</p>
          </div>
          <div className="code glass">
            <div className="code-head"><span>Terminal</span><span>bash</span></div>
            <pre>{`# Clone the repository
git clone https://github.com/pal404error/sift.git
cd sift

# Install locally
pip install -e .

# Start the server (fakes enabled by default for zero-config testing)
sift serve

# Or deploy using Docker Compose
docker compose up -d`}</pre>
          </div>
        </section>

        <section className="section" id="faq">
          <div className="section-head">
            <span className="kicker">Q & A</span>
            <h2>Frequently Asked Questions</h2>
            <p>Common questions about architecture, hosting, and features.</p>
          </div>
          <div className="faq">
            {FAQ.map((item) => (
              <details key={item.q}>
                <summary>{item.q}</summary>
                <div className="faq-content">{item.a}</div>
              </details>
            ))}
          </div>
        </section>

        <section className="section cta">
          <span className="kicker">The Verdict</span>
          <h2>Ready To Self-Host?</h2>
          <p>Bring your own models. Keep your own data. MIT licensed, forever.</p>
          <div className="hero-actions">
            <a href="https://github.com/pal404error/sift" className="btn primary">Star On GitHub</a>
            <a href="https://github.com/pal404error/sift/blob/main/README.md" className="btn ghost">Read The Docs</a>
          </div>
        </section>
      </main>

      <footer className="foot">
        <div className="foot-grid">
          <div>
            <h4>Product</h4>
            <a href="#features">Features</a>
            <a href="#how">How It Works</a>
            <a href="https://github.com/pal404error/sift/blob/main/CHANGELOG.md">Changelog</a>
          </div>
          <div>
            <h4>Developers</h4>
            <a href="https://github.com/pal404error/sift">GitHub</a>
            <a href="https://github.com/pal404error/sift/blob/main/README.md">Documentation</a>
            <a href="https://github.com/pal404error/sift/blob/main/CONTRIBUTING.md">Contributing</a>
          </div>
          <div>
            <h4>Community & Legal</h4>
            <a href="https://github.com/pal404error/sift/blob/main/CODE_OF_CONDUCT.md">Code Of Conduct</a>
            <a href="https://github.com/pal404error/sift/blob/main/SECURITY.md">Security</a>
            <a href="https://github.com/pal404error/sift/blob/main/LICENSE">MIT License</a>
          </div>
        </div>
        <div className="foot-bottom">
          <span>Released Under The MIT License</span>
          <span>Built By <a href="https://github.com/pal404error">pal404error</a></span>
        </div>
      </footer>
    </div>
  );
}
