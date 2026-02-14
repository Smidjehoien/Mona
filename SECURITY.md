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

## Known Limitations

This is an educational exercise application with the following limitations:

1. **No Authentication**: The API does not implement authentication or authorization
2. **No Rate Limiting**: Endpoints are not rate-limited
3. **In-Memory Storage**: All data is lost on application restart
4. **No HTTPS**: Application runs on HTTP (production should use HTTPS)
5. **No Data Encryption**: Data is not encrypted at rest or in transit

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
- No critical security issues identified
- All security best practices for educational applications followed

---

**Note**: This is an educational exercise application. It should not be deployed to production without implementing additional security measures including authentication, authorization, HTTPS, rate limiting, and data encryption.
