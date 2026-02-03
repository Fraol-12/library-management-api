# Library Management API

Production-style REST API for a library system
## Authentication & Authorization

### Endpoints
- POST /api/register/ → Create account + auto-login (returns tokens)
  Body: {"username", "email", "password", "password2"}
- POST /api/token/ → Login (username + password → tokens)
- POST /api/token/refresh/ → Refresh access token
- GET /api/me/ → Current user info (requires Bearer token)

### Roles
- Regular users (borrowers): can borrow/return their own books
- Staff (is_staff=True): full book management, view all loans, force returns

### Public access
- Catalog browsing (GET /books/) will be open (no token needed)