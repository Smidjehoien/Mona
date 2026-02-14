# Security Policy

## Security Status

This document outlines the security measures and status of the Mergington High School API.

### Last Security Audit: 2026-02-14

## Dependency Security ✅

All project dependencies have been scanned for known vulnerabilities using the GitHub Advisory Database:

| Package | Version | Status |
|---------|---------|--------|
| fastapi | 0.129.0 | ✅ No known vulnerabilities |
| uvicorn | 0.40.0 | ✅ No known vulnerabilities |
| pytest | 9.0.2 | ✅ No known vulnerabilities |
| httpx | 0.28.1 | ✅ No known vulnerabilities |

## Code Security Measures

### Input Validation ✅
- **Email Validation**: All email inputs are validated using regex pattern `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Activity Name Validation**: Activity names are checked against a whitelist (existing activities)
- **Duplicate Prevention**: Students cannot sign up for the same activity twice

### Frontend Security ✅
- **XSS Prevention**: Uses `textContent` instead of `innerHTML` for dynamic content (line 224 in app.js)
- **URL Encoding**: All query parameters are properly encoded using `encodeURIComponent()`
- **User Confirmation**: Delete operations require user confirmation before execution

### API Security ✅
- **HTTP Status Codes**: Proper status codes for all responses (400, 404, 200)
- **Error Messages**: Descriptive error messages without exposing sensitive information
- **Data Validation**: All endpoints validate input before processing

### Data Handling ✅
- **In-Memory Storage**: No persistent storage of sensitive data
- **No Authentication**: This is a school exercise - not production system
- **Email Pattern**: Follows standard email format validation

## Code Security Analysis Results

### OWASP Top 10 Assessment

| Category | Status | Notes |
|----------|--------|-------|
| SQL Injection | ✅ SAFE | No database used; in-memory storage only |
| Command Injection | ✅ SAFE | No shell commands or subprocess calls |
| XSS | ✅ SAFE | Frontend uses `textContent` not `innerHTML` |
| Path Traversal | ⚠️ LOW | Static files properly scoped to `static/` directory |
| Insecure Deserialization | ✅ SAFE | Uses FastAPI's safe JSON handling |
| Broken Access Control | ⚠️ INTENTIONAL | No auth required (educational exercise) |
| Cryptographic Failures | ✅ N/A | No sensitive data stored |
| Information Disclosure | ⚠️ LOW | Error messages could be more generic |
| CORS | ✅ SAFE | Same-Origin Policy enforced by default |
| Logging/Monitoring | ⚠️ LIMITED | No audit logging (acceptable for exercise) |

### Security Strengths ✅

1. **No SQL Injection**: In-memory storage eliminates database injection risks
2. **No Command Injection**: No system calls or subprocess execution
3. **XSS Prevention**: Client-side code properly uses `textContent` instead of `innerHTML`
4. **Safe Deserialization**: FastAPI's JSON handling is secure
5. **Input Validation**: Email format validated with regex on all endpoints
6. **URL Encoding**: All query parameters properly encoded in frontend

### Known Limitations (Educational Exercise)

This is an educational exercise application with the following intentional limitations:

1. **No Authentication**: The API does not implement authentication or authorization
   - Anyone can sign up/unregister any student
   - Skills endpoint allows viewing any student's data
   - **Note**: This is intentional for the learning exercise
   
2. **No Rate Limiting**: Endpoints are not rate-limited
   - Could allow email enumeration
   - Could be subject to DoS attacks
   
3. **In-Memory Storage**: All data is lost on application restart
   - No persistence layer
   - No transaction support
   
4. **No HTTPS**: Application runs on HTTP (production should use HTTPS)
   - Data transmitted in clear text
   
5. **No Data Encryption**: Data is not encrypted at rest or in transit

6. **Email Validation**: Current regex pattern could be stricter
   - Allows some edge cases like consecutive dots
   - Recommendation: Use more restrictive pattern for production

## Security Best Practices Applied

- ✅ Input validation on all endpoints
- ✅ Proper error handling without information disclosure
- ✅ XSS prevention in frontend code
- ✅ URL encoding for all dynamic parameters
- ✅ Dependencies kept up-to-date with no known vulnerabilities
- ✅ Comprehensive test coverage including security-related tests

## Reporting Security Issues

This is an educational project. For a production system, security issues should be reported through responsible disclosure channels.

## Security Testing

### Automated Tests
- 15 unit tests covering all endpoints
- Input validation tests (invalid email, missing activity, etc.)
- Duplicate signup prevention tests
- Capacity limit enforcement tests

### Manual Security Review
- Code review completed: 2026-02-14
- OWASP Top 10 assessment completed
- No critical security issues for educational use
- All identified risks are intentional design choices or acceptable for non-production use

### Security Scan Results

✅ **Dependency Vulnerabilities**: None found (all 4 dependencies clean)  
✅ **SQL Injection**: Not applicable (no database)  
✅ **Command Injection**: Not applicable (no system calls)  
✅ **XSS**: Protected (proper use of textContent)  
✅ **Deserialization**: Safe (FastAPI JSON handling)  
⚠️ **Authentication**: Intentionally omitted (educational exercise)  
⚠️ **Rate Limiting**: Not implemented (acceptable for exercise)  
⚠️ **Access Control**: Not implemented (intentional design choice)

### Risk Assessment

**For Educational Use**: ✅ **SECURE**  
**For Production Use**: ❌ **NOT RECOMMENDED** without implementing:
- Authentication and authorization
- HTTPS/TLS encryption
- Rate limiting
- Audit logging
- Data persistence with encryption
- Input sanitization improvements
- CSRF protection
- Security headers (CSP, X-Frame-Options, etc.)

---

**Note**: This is an educational exercise application. It should not be deployed to production without implementing additional security measures including authentication, authorization, HTTPS, rate limiting, and data encryption.
