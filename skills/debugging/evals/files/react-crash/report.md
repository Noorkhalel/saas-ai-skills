# Bug report: app crashes right after login — for some users

**Reported:** Users signing in with Google get a blank white screen immediately after login.
Users who sign up with email + password do not have the problem — it works fine for them.
It started after we shipped the new "Password set {date}" line in the profile widget last week.

**Frequency:** 100% for Google sign-in accounts; 0% for email/password accounts.

**Browser console (from an affected user):**

```
Uncaught TypeError: Cannot read properties of null (reading 'toLocaleDateString')
    at ProfileWidget (ProfileWidget.tsx:20:44)
    at renderWithHooks (react-dom.development.js:15486)
    at mountIndeterminateComponent (react-dom.development.js:20103)
    ...
The above error occurred in the <ProfileWidget> component.
React will try to recreate this tree from scratch using the error boundary.
```

**Relevant API response shape** — `GET /api/auth/me`:

For an email/password user:
```json
{ "id": "u_1", "name": "Ana", "avatarUrl": "https://…/a.png", "passwordUpdatedAt": "2025-11-02T10:00:00Z" }
```

For a Google (social) user:
```json
{ "id": "u_2", "name": "Ben", "avatarUrl": "https://…/b.png", "passwordUpdatedAt": null }
```

Component source is in `ProfileWidget.tsx` (same folder).
