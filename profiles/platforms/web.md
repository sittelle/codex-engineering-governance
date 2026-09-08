# Web Application Profile

Browser/client is untrusted. Establish exposure explicitly. External production traffic uses authenticated encrypted transport. Authoritative authz is server-side.

Evaluate session security, CSRF, CORS, validation, output encoding, injection, file uploads, safe errors, security headers/CSP, limits/timeouts/rate abuse, diagnostic endpoint exposure, and security logging.

SA2 externally reachable web normally requires threat model, security tests, SAST/SCA/secrets, manual authz review, and DAST where practical.
