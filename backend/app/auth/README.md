# Authentication System

## Magic Link Authentication Flow

### 1. Request Magic Link

- **Route**: [POST /api/auth/request](../routers/auth.py)
- **Input**: Email address
- **Process**:
  - Rate limiting: 2 requests per 10 minutes per email (in-memory)
  - Validates email exists in accounts table
  - Generates 32-byte URL-safe tokens (magic link + device nonce)
  - Stores SHA-256 hashed token (e.g., not raw token) in database with expiry
  - Sets device nonce cookie for device binding (2hr max age)
  - Sends email with magic link (configurable via SEND_EMAIL) with the raw token
  - Returns 200 regardless of email validity (prevents user enumeration)

### 2. Consume Magic Link

- **Route**: [GET /api/auth](../routers/auth.py)
- **Input**: Magic link token (query parameter)
- **Process**:
  - Validates device nonce cookie matches stored hash
  - Atomically validates + consumes token (prevents reuse)
  - Creates authenticated session with user_id
  - Handles specific error cases (expired, used, device mismatch)

## Session & Validation

- Sessions are signed cookies (not encrypted) and include user_id; player sessions include player_id and world_id.
- User requests that operate on world-scoped data require `X-World-Id`.
- Core request/WS validation helpers live in `app/dependencies.py` and enforce:
  - valid user session
  - world scoping for user endpoints
  - player-only access for player endpoints
  - websocket session parsing for realtime routes
