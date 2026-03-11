# Security Policy

## Overview

This is an **educational exercise** for learning GitHub Copilot. Security features are intentionally simplified.

## Automated Security Checks

Security scanning runs automatically via `.github/workflows/security.yml`:
- Dependency vulnerability scanning
- CodeQL static analysis  
- Bandit security linting
- Weekly scheduled scans

## Security Status

**Dependencies**: No known vulnerabilities (last checked: 2026-02-14)  
**Code**: XSS protection, input validation implemented

## Intentional Limitations

This educational app lacks production security features:
- No authentication/authorization
- No rate limiting
- No HTTPS/encryption
- In-memory storage (no persistence)

## Production Deployment

**DO NOT deploy as-is.** Required additions:
- User authentication & authorization
- HTTPS/TLS
- Rate limiting
- Database with encrypted data
- CSRF protection
- Security headers

## Reporting Issues

For educational purposes only. Real applications should have a responsible disclosure process.
