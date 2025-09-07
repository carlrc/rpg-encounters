# Authentication System

## Magic Link Authentication Flow

### 1. Request Magic Link
- **Route**: `POST /auth/request`
- **Input**: Email address + redirect URL
- **Process**:
  - Validates email exists in accounts table
  - Generates device nonce cookie (for device binding)
  - Creates magic link with SHA-256 hashed token
  - Returns success (no user enumeration)

### 2. Consume Magic Link
- **Route**: `POST /auth/consume`  
- **Input**: Magic link token
- **Process**:
  - Validates device nonce cookie matches
  - Atomically validates + consumes token
  - Creates authenticated session
  - Returns redirect URL

### 3. Session Management
- **Cookie-based sessions** using FastAPI SessionMiddleware
- **7-day expiry** with automatic cleanup
- **Secure defaults**: httpOnly, secure, SameSite=lax

## Key Security Features

- **Token Hashing**: Raw tokens never stored, only SHA-256 hashes
- **Device Binding**: Soft binding via device nonce cookies
- **Single Use**: Tokens consumed atomically, prevent race conditions
- **No User Enumeration**: Same response for existing/non-existing emails
- **Open Redirect Protection**: Only relative URLs allowed
- **10-minute Expiry**: Magic links expire quickly
