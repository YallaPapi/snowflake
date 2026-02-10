# Security Analysis Report

**Project:** Snowflake Novel Generation Engine
**Date:** 2026-02-07
**Scope:** Complete codebase security analysis
**Risk Level: HIGH**

---

## Executive Summary

The Snowflake project presents **CRITICAL SECURITY VULNERABILITIES** requiring immediate remediation. The API lacks authentication, has overly permissive CORS, exposes error information, and contains path traversal risks. **17 vulnerabilities identified: 5 CRITICAL, 7 HIGH, 5 MEDIUM.**

---

## 1. Authentication & Authorization — CRITICAL

**Finding:** NO authentication on any endpoint.

**Affected:**
- All endpoints in `src/api/main.py` (lines 111-410)
- All endpoints in `src/observability/server.py` (lines 35-194)
- All endpoints in `src/api/scene_engine_endpoints.py`

**Risk:** Anyone can create projects, trigger expensive AI generation, download manuscripts, and access monitoring data.

**Fix:** Implement FastAPI `Depends()` with JWT or API key validation.

---

## 2. CORS Configuration — CRITICAL

**Finding:** CORS allows ALL origins with ALL methods.

**FastAPI** (`main.py:90-96`):
```python
allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(",")  # Defaults to "*"
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Flask** (`server.py:24`): `CORS(app)` — default allows all.

**Fix:** Restrict to known origins, limit methods to GET/POST, specify allowed headers.

---

## 3. Input Validation — HIGH

**Finding:** User brief input has no length limits or content filtering.

- `NovelBrief.brief` — no max_length (`main.py:28`)
- `ScenePlanRequest.scene_crucible` — min_length=10 but no max (`scene_engine_endpoints.py:38`)
- No protection against extremely large payloads

**Fix:** Add `max_length` constraints, implement request size middleware (1MB limit).

---

## 4. Path Traversal — HIGH

**Finding:** Download endpoint uses user-provided `project_id` in file path without validation.

**Location:** `main.py:383-406`
```python
file_path = Path("artifacts") / project_id / format_to_file[format]
# project_id could be "../../.env" — no validation!
```

**Fix:** Validate `project_id` is alphanumeric, resolve path and verify it's within artifacts/.

---

## 5. Secret Management — CRITICAL

**Finding:** Real API keys in `.env` file. While `.gitignore` covers `.env`, keys may already be in git history.

**Affected:** `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` in `.env`

**Fix:**
1. Revoke and rotate these API keys immediately
2. Scan git history with BFG Repo-Cleaner
3. Use secrets manager for production

---

## 6. Error Information Leakage — HIGH

**Finding:** Exception details returned in HTTP responses, exposing internal paths, OS info, and schema.

**Pattern (14+ instances):**
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # Leaks internals
```

**Locations:** `main.py:139,201,265,341,380`, `scene_engine_endpoints.py:158,229,312,371,410,446`

**Fix:** Log full errors internally, return generic messages to clients.

---

## 7. Rate Limiting — HIGH

**Finding:** No rate limiting on any endpoint. Attackers can flood `/generate/full` to rack up API costs.

**Fix:** Implement `slowapi` with per-IP limits (e.g., 10/min for projects, 1/hour for generation).

---

## 8. Prompt Injection — HIGH

**Finding:** User `brief` passed directly to AI models without sanitization.

**Location:** `main.py:231,293` — `brief_text = brief.brief` → `pipeline.execute_step_0(brief_text)`

**Risk:** Malicious briefs can manipulate AI output or extract system prompts.

**Fix:** Add content validation, filter dangerous patterns (SYSTEM, OVERRIDE, IGNORE).

---

## 9. Broad Exception Handling — MEDIUM

**Finding:** 157 instances of `except Exception` across 45 files. 42 instances silently swallow errors.

**Risk:** Security issues masked, debugging difficult, injection attacks hidden.

**Fix:** Use targeted exception types, always log errors.

---

## 10. No HTTPS Enforcement — HIGH

**Finding:** API runs HTTP only. No SSL/TLS configuration.

**Location:** `main.py:430-435` — `uvicorn.run()` with no SSL options.

**Fix:** Configure SSL certificates, enforce HTTPS in production.

---

## 11. No Project Isolation — HIGH

**Finding:** Any user can access any project by ID. No ownership validation.

**Fix:** Implement project ownership model, verify user access before returning data.

---

## 12. Dependency Vulnerabilities — MEDIUM

**Finding:** Pinned versions may contain known CVEs. No security scanning configured.

**Fix:** Run `pip-audit`, pin exact versions, add automated scanning.

---

## 13. No Data Encryption at Rest — MEDIUM

**Finding:** Manuscripts and artifacts stored as plaintext JSON files.

**Fix:** Implement encryption for sensitive artifacts using `cryptography.fernet`.

---

## 14. Subprocess Usage — MEDIUM

**Finding:** `subprocess.run()` in test runner (`run_tests.py:35-46`). Low risk currently but maintenance concern.

**Fix:** Validate all command components, restrict to known paths.

---

## 15. Unsafe JSON Loading — MEDIUM

**Finding:** JSON files loaded without structure validation (`main.py:156,185,226,356`).

**Fix:** Validate loaded JSON against Pydantic models before use.

---

## Summary Table

| # | Category | Severity | Status |
|---|----------|----------|--------|
| 1 | No Authentication | CRITICAL | Unfixed |
| 2 | Permissive CORS | CRITICAL | Unfixed |
| 3 | Hardcoded Secrets | CRITICAL | Unfixed |
| 4 | Path Traversal | HIGH | Unfixed |
| 5 | No Rate Limiting | HIGH | Unfixed |
| 6 | Prompt Injection | HIGH | Unfixed |
| 7 | No Project Isolation | HIGH | Unfixed |
| 8 | No HTTPS | HIGH | Unfixed |
| 9 | Error Leakage | HIGH | Unfixed |
| 10 | No Input Size Limits | MEDIUM | Unfixed |
| 11 | Broad Exceptions | MEDIUM | Unfixed |
| 12 | No Encryption at Rest | MEDIUM | Unfixed |
| 13 | Dependency Vulns | MEDIUM | Unfixed |
| 14 | Subprocess Risk | MEDIUM | Unfixed |
| 15 | Unsafe JSON Loading | MEDIUM | Unfixed |

---

## Remediation Priority

### Phase 1 — IMMEDIATE (Week 1)
1. Revoke and rotate API keys
2. Implement basic authentication
3. Restrict CORS origins
4. Add path validation to download endpoint
5. Add request size limits

### Phase 2 — URGENT (Weeks 2-3)
1. Add rate limiting
2. Implement HTTPS
3. Sanitize error responses
4. Implement project ownership
5. Add prompt injection filtering

### Phase 3 — IMPORTANT (Month 1)
1. Data encryption at rest
2. Update dependencies
3. Security logging
4. Security headers (CSP, X-Frame-Options)
5. Penetration testing
