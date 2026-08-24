import React, { useState } from "react";
import * as ThreeUI from "@designcodeio/threeui";
import { ThreeUIBoundary } from "./ThreeUIBoundary";

const T = ThreeUI as any;

const INSTALL = 'pip install "sift @ git+https://github.com/pal404error/sift.git"';
const INSTALL_DOCKER = "docker compose up -d";

const FEATURES = [
  { n: "01", title: "Pluggable Providers", body: "Swap LLMs and embeddings via config. First-class OpenAI, Anthropic, Ollama support, plus fakes for local testing." },
  { n: "02", title: "Flexible Storage", body: "Store your vector embeddings in-memory for quick iteration, or scale seamlessly with built-in Qdrant vector store integration." },
  { n: "03", title: "Enterprise Security", body: "Deploy confidently with OIDC/JWKS authentication, API-key Role Based Access Control (RBAC), and a comprehensive audit log." },
  { n: "04", title: "Advanced Retrieval", body: "Achieve higher precision by combining lexical search with cross-encoder rerankers for top-tier semantic accuracy." },
  { n: "05", title: "Concurrent Crawler", body: "Built-in crawl orchestrator fully respects robots.txt, supports ETags, and enables incremental updates to keep your index fresh." },
  { n: "06", title: "Ops & Monitoring", body: "Ships with a powerful CLI, static web UI, offline eval harness, /metrics and /health probes for Prometheus + Grafana." },
];

const STEPS = [
  { n: "I", title: "Ingest & Crawl", body: "The orchestrator concurrently pulls pages from your sources, respecting robots.txt and gracefully handling incremental re-crawls via ETags." },
  { n: "II", title: "Embed & Store", body: "Content is intelligently chunked, passed through your chosen embedding provider, and indexed into your active vector store." },
  { n: "III", title: "Retrieve & Generate", body: "Queries are vectorized, optionally reranked with cross-encoders, and answered by your preferred LLM with transparent sources attached." },
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
  const [method, setMethod] = useState<"pip" | "docker">("pip");
  const [hero3dFailed, setHero3dFailed] = useState(false);
  const [badgeFailed, setBadgeFailed] = useState(false);

  const code = method === "pip" ? INSTALL : INSTALL_DOCKER;

  function copyInstall() {
    navigator.clipboard?.writeText(code).then(() => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="page">
      <div className="dateline container">
        <span>The Open-Source Search Edition</span>
        <span>Est. 2026 &middot; Vol. 1 — No. 1</span>
        <span>Self-Hosted &middot; MIT</span>
      </div>

      <header className="masthead container">
        <h1 className="title">Sift</h1>
        <p className="tagline">Enterprise, Self-Hostable, Multi-Provider RAG Search Engine</p>
        {badgeFailed ? (
          <span className="hero-badge-fallback">MIT Licensed</span>
        ) : (
          <ThreeUIBoundary fallback={<span className="hero-badge-fallback">MIT Licensed</span>} onError={() => setBadgeFailed(true)}>
            <T.SparkBadge className="hero-badge" />
          </ThreeUIBoundary>
        )}
      </header>

      <div className="topnav-row container">
        <nav className={menuOpen ? "topnav active" : "topnav"} id="nav-links">
          <a href="#features" onClick={() => setMenuOpen(false)}>Features</a>
          <a href="#how" onClick={() => setMenuOpen(false)}>How It Works</a>
          <a href="#quickstart" onClick={() => setMenuOpen(false)}>Quickstart</a>
          <a href="#faq" onClick={() => setMenuOpen(false)}>FAQ</a>
          <a href="https://github.com/pal404error/sift#readme" onClick={() => setMenuOpen(false)}>Docs</a>
        </nav>
        <a href="https://github.com/pal404error/sift" className="btn" style={{ fontSize: "0.75rem", padding: "0.5rem 1rem" }}>GitHub</a>
        <button className="menu-toggle" onClick={() => setMenuOpen((v) => !v)} aria-label="Toggle menu">MENU</button>
      </div>

      <main>
        <section className="hero" id="home">
          <div className="container">
            <span className="kicker">Front Page &middot; The Search Story</span>
            <h1>Intelligence, Grounded.</h1>
            <p className="deck">The enterprise-ready, self-hostable multi-provider RAG search engine. Bring your own models, keep your own data, and answer with source-backed retrieval.</p>

            <div className="exhibit">
              <div className="exhibit-frame">
                {hero3dFailed ? (
                  <div className="exhibit-fallback" />
                ) : (
                  <ThreeUIBoundary fallback={<div className="exhibit-fallback" />} onError={() => setHero3dFailed(true)}>
                    <T.TopoField className="hero-3d" style={{ width: "100%", height: "100%" }} />
                  </ThreeUIBoundary>
                )}
              </div>
              <span className="exhibit-caption">Fig. 1 — The Retrieval Field (ThreeUI)</span>
            </div>

            <div className="hero-actions">
              <a href="#quickstart" className="btn">Get Started</a>
              <a href="https://github.com/pal404error/sift" className="btn btn-outline">GitHub Repository</a>
            </div>

            <div className="install-box">
              <code>{code}</code>
              <button onClick={copyInstall}>{copied ? "Copied!" : "Copy"}</button>
            </div>

            <div className="method-switch">
              <button className={method === "pip" ? "active" : ""} onClick={() => setMethod("pip")}>pip</button>
              <button className={method === "docker" ? "active" : ""} onClick={() => setMethod("docker")}>docker</button>
            </div>
          </div>
        </section>

        <section className="section" id="features">
          <div className="section-head">
            <span className="kicker">In This Edition</span>
            <h2>Everything You Need To Ship Search</h2>
            <p>A clean, pluggable foundation — not a walled garden. Wire in your stack and stay in control.</p>
          </div>
          <div className="grid-6">
            {FEATURES.map((f) => (
              <article className="feature-card" key={f.title}>
                <div className="ficon">{f.n}</div>
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
            <p>Three movements between your sources and a grounded answer.</p>
          </div>
          <div className="steps">
            {STEPS.map((s) => (
              <div className="step" key={s.n}>
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
          <div className="code-block-wrapper">
            <div className="code-header"><span>Terminal</span><span>bash</span></div>
            <pre className="code-block">{`# Clone the repository
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
            <span className="kicker">Corrections &amp; Clarifications</span>
            <h2>Frequently Asked Questions</h2>
            <p>Common questions about architecture, hosting, and features.</p>
          </div>
          <div className="faq-list">
            {FAQ.map((item) => (
              <details key={item.q}>
                <summary>{item.q}</summary>
                <div className="faq-content">{item.a}</div>
              </details>
            ))}
          </div>
        </section>

        <section className="section cta-section">
          <div className="container">
            <span className="kicker">The Verdict</span>
            <h2>Ready To Self-Host?</h2>
            <p style={{ marginTop: "0.75rem", color: "var(--ink-soft)" }}>Bring your own models. Keep your own data. MIT licensed, forever.</p>
            <div className="hero-actions">
              <a href="https://github.com/pal404error/sift" className="btn">Star On GitHub</a>
              <a href="https://github.com/pal404error/sift/blob/main/README.md" className="btn btn-outline">Read The Docs</a>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="container">
          <div className="footer-grid">
            <div className="footer-col">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#how">How It Works</a>
              <a href="https://github.com/pal404error/sift/blob/main/CHANGELOG.md">Changelog</a>
            </div>
            <div className="footer-col">
              <h4>Developers</h4>
              <a href="https://github.com/pal404error/sift">GitHub</a>
              <a href="https://github.com/pal404error/sift/blob/main/README.md">Documentation</a>
              <a href="https://github.com/pal404error/sift/blob/main/CONTRIBUTING.md">Contributing</a>
            </div>
            <div className="footer-col">
              <h4>Community &amp; Legal</h4>
              <a href="https://github.com/pal404error/sift/blob/main/CODE_OF_CONDUCT.md">Code Of Conduct</a>
              <a href="https://github.com/pal404error/sift/blob/main/SECURITY.md">Security</a>
              <a href="https://github.com/pal404error/sift/blob/main/LICENSE">MIT License</a>
            </div>
          </div>
          <div className="footer-bottom">
            <span>Released Under The MIT License</span>
            <span>Built By pal404error</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
