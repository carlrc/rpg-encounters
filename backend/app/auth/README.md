# Authentication System

## Magic Link Authentication Flow

### 1. Request Magic Link
- **Route**: `POST /api/auth/request`
- **Input**: Email address
- **Process**:
  - Rate limits: 2 requests per 10 minutes per email
  - Validates email exists in accounts table
  - Generates 32-byte URL-safe tokens (magic link + device nonce)
  - Stores SHA-256 hashed tokens in database
  - Sets device nonce cookie for device binding
  - Returns 200 regardless of email validity (prevents user enumeration)

### 2. Consume Magic Link
- **Route**: `GET /api/auth` 
- **Input**: Magic link token (query parameter)
- **Process**:
  - Validates device nonce cookie matches stored hash
  - Atomically validates + consumes token (row-level locking)
  - Creates authenticated session with user_id
  - Handles specific error cases (expired, used, device mismatch)

### 3. Session Management
- **Cookie-based sessions** using [Starlette SessionMiddleware](# https://www.starlette.io/middleware/#sessionmiddleware)
