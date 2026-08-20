---
name: security-review
description: OWASP Top 10, secret scanning, input sanitization, dependency audit.
trigger: Before merge, on new endpoints, on new dependencies, after scraping/ingestion.
discipline: Untrusted input is hostile. No secrets in code. Audit every dependency.
---

# Security Review

Goal: catch vulnerabilities before they reach production.

## Checklist
1. **Secrets:** no hardcoded keys/tokens/connection strings. Use `.env` + manager.
   Run secret scan (`gitleaks`/`detect-secrets`) in pre-commit + CI.
2. **Input validation:** all user queries, uploaded docs, and scraped HTML validated and
   sanitized (Pydantic models; HTML sanitizer for web content → XSS defense).
3. **Injection:** parameterize DB/vector queries; never interpolate untrusted text into
   prompts without escaping; guard against prompt injection from retrieved content.
4. **AuthN/AuthZ:** protect endpoints; verify `api-key`/bearer; least privilege.
5. **Dependencies:** `pip-audit` / `npm audit` / `cargo audit` on every PR; pin versions.
6. **Rate limiting & abuse:** throttle LLM/embedding calls; cap payload sizes.
7. **Logging:** never log secrets or full PII; redact.
8. **SAST:** run CodeQL/semgrep in CI (differentiator per trending-insights §3.4).

## OWASP Top 10 (quick map)
A01 Broken Access Control · A02 Crypto Failures · A03 Injection · A05 Misconfig ·
A07 Auth Failures · A10 SSRF (relevant when fetching web content).

## Output
A short security note: scanned? deps audited? inputs sanitized? blockers (if any).
Block merge on critical/high findings.
