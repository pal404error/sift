# Security Policy

Security is a top priority for Sift, especially since we are dealing with enterprise data and search infrastructure. 

## Supported Versions

Currently, the `main` branch and the latest stable release are supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| v0.1.x  | :white_check_mark: |

## Reporting a Vulnerability

Please **do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in Sift, please report it privately by sending an email to **security@pal404error.local** (or direct message the maintainers). 

We take all disclosures seriously and will respond within 48 hours to acknowledge the report. We will work with you to understand the issue, provide a timeline for a fix, and coordinate a secure release.

## Enterprise Security Features

When deploying Sift in an enterprise environment, we highly recommend utilizing the built-in security features:

- **OIDC / SSO Integration**: Sift supports OpenID Connect. Ensure you configure your `.env` to enforce authentication for all API endpoints and the Web UI.
- **Audit Logging**: Enable verbose audit logging to track query histories, administrative actions, and data source modifications.
- **Network Isolation**: Run the vector store and application layers in private subnets, exposing only the necessary application gateways.

Thank you for helping keep the Sift community and its users secure!
