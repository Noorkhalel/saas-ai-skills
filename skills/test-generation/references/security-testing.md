# Security Testing

## Important Context

Security test suggestions are generated as part of comprehensive test coverage for code that handles authentication, authorization, input validation, and data access control. These tests should be run in authorized testing environments only. They verify that security controls work correctly — they are defensive tests, not offensive exploits.

## SQL Injection

Test that user input is never interpolated directly into SQL:

```typescript
describe('SQL injection prevention', () => {
  it('handles malicious input in search parameter', async () => {
    const response = await request(app)
      .get('/users')
      .query({ search: "'; DROP TABLE users; --" });

    // Should return safely (empty results or 400), not crash
    expect([200, 400]).toContain(response.status);
    // Verify users table still exists by making another request
    const check = await request(app).get('/users');
    expect(check.status).toBe(200);
  });

  it('parameterizes queries for user-supplied IDs', async () => {
    const response = await request(app).get("/users/1' OR '1'='1");

    expect(response.status).toBe(400); // or 404, not 200 with all users
  });
});
```

## Cross-Site Scripting (XSS)

Test that user-generated content is properly escaped in output:

```typescript
it('escapes HTML in user-submitted content', async () => {
  await createPost({ content: '<script>alert("xss")</script>' });

  const response = await request(app).get('/posts');
  const html = response.text;

  expect(html).not.toContain('<script>');
  expect(html).toContain('&lt;script&gt;'); // Escaped
});

it('escapes HTML in API JSON responses', async () => {
  await createUser({ name: '<img src=x onerror=alert(1)>' });

  const response = await request(app).get('/api/users');
  const user = response.body[0];

  // Name should be stored as-is but rendered escaped
  expect(user.name).toBe('<img src=x onerror=alert(1)>');
  // The rendering layer (frontend) must escape this
});
```

## Cross-Site Request Forgery (CSRF)

```typescript
it('rejects state-changing requests without CSRF token', async () => {
  const response = await request(app)
    .post('/users')
    .send({ name: 'Test' });
    // No CSRF token header

  expect(response.status).toBe(403);
});

it('accepts requests with valid CSRF token', async () => {
  // Get CSRF token from the server
  const tokenResponse = await request(app).get('/csrf-token');
  const csrfToken = tokenResponse.body.token;

  const response = await request(app)
    .post('/users')
    .set('X-CSRF-Token', csrfToken)
    .send({ name: 'Test' });

  expect(response.status).toBe(201);
});
```

## Server-Side Request Forgery (SSRF)

```typescript
it('rejects requests to internal network addresses', async () => {
  const response = await request(app)
    .post('/fetch-url')
    .send({ url: 'http://169.254.169.254/metadata' }); // AWS metadata

  expect(response.status).toBe(400);
  expect(response.body.error).toMatch(/blocked|denied|invalid/i);
});

it('rejects localhost URLs', async () => {
  const response = await request(app)
    .post('/fetch-url')
    .send({ url: 'http://localhost:3000/admin' });

  expect(response.status).toBe(400);
});
```

## Input Validation

```typescript
describe('Input validation', () => {
  it('rejects oversized payloads', async () => {
    const response = await request(app)
      .post('/upload')
      .send({ data: 'x'.repeat(10_000_000) });

    expect(response.status).toBe(413);
  });

  it('sanitizes file names', async () => {
    const response = await request(app)
      .post('/upload')
      .attach('file', Buffer.from('data'), '../../../etc/passwd');

    // Should not allow path traversal
    expect(response.status).toBe(400);
  });

  it('rejects unexpected content types', async () => {
    const response = await request(app)
      .post('/api/data')
      .set('Content-Type', 'application/xml')
      .send('<data>test</data>');

    expect(response.status).toBe(415);
  });
});
```

## Authentication

```typescript
describe('Authentication', () => {
  it('returns 401 for missing credentials', async () => {
    const response = await request(app).get('/protected');
    expect(response.status).toBe(401);
  });

  it('returns 401 for expired token', async () => {
    const expiredToken = createToken({ exp: Date.now() / 1000 - 3600 });
    const response = await request(app)
      .get('/protected')
      .set('Authorization', `Bearer ${expiredToken}`);

    expect(response.status).toBe(401);
  });

  it('returns 401 for malformed token', async () => {
    const response = await request(app)
      .get('/protected')
      .set('Authorization', 'Bearer not-a-real-token');

    expect(response.status).toBe(401);
  });

  it('does not reveal whether email exists on login failure', async () => {
    const responseWrongEmail = await request(app)
      .post('/login')
      .send({ email: 'nonexistent@test.com', password: 'wrong' });

    const responseWrongPassword = await request(app)
      .post('/login')
      .send({ email: 'existing@test.com', password: 'wrong' });

    // Same status and error message for both — no email enumeration
    expect(responseWrongEmail.status).toBe(401);
    expect(responseWrongPassword.status).toBe(401);
    expect(responseWrongEmail.body.error).toBe(responseWrongPassword.body.error);
  });
});
```

## Authorization and RBAC

```typescript
describe('Role-based access control', () => {
  it('admin can access admin panel', async () => {
    const response = await request(app)
      .get('/admin')
      .set('Authorization', `Bearer ${adminToken}`);

    expect(response.status).toBe(200);
  });

  it('member cannot access admin panel', async () => {
    const response = await request(app)
      .get('/admin')
      .set('Authorization', `Bearer ${memberToken}`);

    expect(response.status).toBe(403);
  });

  it('user can only access own resources', async () => {
    const response = await request(app)
      .get(`/users/${otherUser.id}/profile`)
      .set('Authorization', `Bearer ${userToken}`);

    expect(response.status).toBe(403);
  });
});
```

## Multi-Tenant Isolation

```typescript
describe('Tenant isolation', () => {
  it('tenant A cannot read tenant B data', async () => {
    const response = await request(app)
      .get('/data')
      .set('Authorization', `Bearer ${tenantAToken}`);

    const ids = response.body.map(d => d.tenantId);
    expect(ids.every(id => id === 'tenant-a')).toBe(true);
    expect(ids).not.toContain('tenant-b');
  });

  it('tenant A cannot update tenant B records', async () => {
    const response = await request(app)
      .patch(`/data/${tenantBRecord.id}`)
      .set('Authorization', `Bearer ${tenantAToken}`)
      .send({ value: 'hijacked' });

    expect(response.status).toBe(404); // or 403
  });

  it('tenant A cannot delete tenant B records', async () => {
    const response = await request(app)
      .delete(`/data/${tenantBRecord.id}`)
      .set('Authorization', `Bearer ${tenantAToken}`);

    expect(response.status).toBe(404); // or 403

    // Verify record still exists
    const check = await request(app)
      .get(`/data/${tenantBRecord.id}`)
      .set('Authorization', `Bearer ${tenantBToken}`);

    expect(check.status).toBe(200);
  });
});
```

## Rate Limiting

```typescript
describe('Rate limiting', () => {
  it('limits login attempts per IP', async () => {
    // Exceed rate limit
    for (let i = 0; i < 6; i++) {
      await request(app).post('/login').send({
        email: 'test@example.com',
        password: 'wrong',
      });
    }

    const response = await request(app).post('/login').send({
      email: 'test@example.com',
      password: 'correct',
    });

    expect(response.status).toBe(429);
  });
});
```
