# Login Flow — Playwright E2E Test Fixture

## Page Description

The login page (`/login`) contains the following elements:

- **Email field**: `<input type="email">` with label "Email address"
- **Password field**: `<input type="password">` with label "Password"
- **"Remember me" checkbox**: Optional, label "Remember me"
- **Submit button**: "Sign In" button
- **"Forgot password?" link**: Navigates to `/forgot-password`
- **Error display**: Alert role element showing error messages
- **Loading state**: Submit button shows "Signing in..." and is disabled during API call

## Flows

### Successful Login
1. User enters valid email and password
2. Clicks "Sign In"
3. Button shows "Signing in..." (disabled)
4. Redirects to `/dashboard`
5. Dashboard shows "Welcome, [Name]" heading

### Failed Login — Invalid Credentials
1. User enters wrong email/password
2. Clicks "Sign In"
3. Error alert shows "Invalid email or password"
4. Password field is cleared, email field retains value
5. User remains on `/login`

### Failed Login — Account Locked
1. User enters correct email but wrong password 5 times
2. After 5th attempt: error shows "Account locked. Try again in 15 minutes."
3. Submit button is disabled

### Failed Login — Empty Fields
1. User clicks "Sign In" without entering anything
2. Inline validation shows "Email is required" under email field
3. Shows "Password is required" under password field
4. No API call is made

### Forgot Password Flow
1. User clicks "Forgot password?"
2. Navigates to `/forgot-password`
3. Page shows "Reset Password" heading
4. Email field and "Send Reset Link" button visible

### Session Persistence (Remember Me)
1. User checks "Remember me" and logs in
2. Closes browser
3. Opens app again — user is still logged in
4. Without "Remember me" — session expires on browser close

## API Contract

```
POST /api/auth/login
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "password123",
  "rememberMe": false
}

Response (200):
{
  "token": "jwt-token",
  "user": { "id": "1", "name": "Jane Doe", "email": "user@example.com" }
}

Response (401):
{ "error": "Invalid email or password" }

Response (423):
{ "error": "Account locked. Try again in 15 minutes." }
```

## Edge Cases

- Email with leading/trailing spaces should be trimmed
- Very long email (>254 chars) should show validation error
- Password with special characters (unicode, emoji) should work
- Network error during login should show "Connection failed. Please try again."
- Concurrent login attempts (double-click) should be debounced
