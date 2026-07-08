# API Testing

## Test Categories

### Success Responses

Test the happy path for each endpoint:

```typescript
it('GET /users returns 200 with list of users', async () => {
  // Arrange — seed test data
  await createTestUser({ name: 'Alice' });
  await createTestUser({ name: 'Bob' });

  // Act
  const response = await request(app).get('/users');

  // Assert
  expect(response.status).toBe(200);
  expect(response.body).toHaveLength(2);
  expect(response.body[0]).toHaveProperty('name');
  expect(response.body[0]).toHaveProperty('id');
});
```

### Error Responses

Test each documented error code:

```typescript
it('GET /users/:id returns 404 for nonexistent user', async () => {
  const response = await request(app).get('/users/nonexistent-id');

  expect(response.status).toBe(404);
  expect(response.body.error).toBeDefined();
});

it('POST /users returns 400 for missing required fields', async () => {
  const response = await request(app)
    .post('/users')
    .send({}); // Missing name, email

  expect(response.status).toBe(400);
  expect(response.body.errors).toContainEqual(
    expect.objectContaining({ field: 'email' })
  );
});
```

### Input Validation

Test validation rules exhaustively:

```typescript
describe('POST /users validation', () => {
  const validUser = { name: 'Test', email: 'test@example.com' };

  it.each([
    ['missing email', { name: 'Test' }, 'email'],
    ['invalid email format', { ...validUser, email: 'not-email' }, 'email'],
    ['name too long', { ...validUser, name: 'a'.repeat(256) }, 'name'],
    ['empty name', { ...validUser, name: '' }, 'name'],
  ])('rejects %s', async (_, body, expectedField) => {
    const response = await request(app).post('/users').send(body);

    expect(response.status).toBe(400);
    expect(response.body.errors).toContainEqual(
      expect.objectContaining({ field: expectedField })
    );
  });
});
```

### Pagination

```typescript
describe('GET /users pagination', () => {
  beforeAll(async () => {
    // Seed 25 test users
    await Promise.all(
      Array.from({ length: 25 }, (_, i) =>
        createTestUser({ name: `User ${i}` })
      )
    );
  });

  it('returns first page with default page size', async () => {
    const response = await request(app).get('/users');
    expect(response.status).toBe(200);
    expect(response.body.data.length).toBeLessThanOrEqual(20); // default page size
    expect(response.body.pagination).toMatchObject({
      page: 1,
      hasMore: true,
    });
  });

  it('returns second page with correct offset', async () => {
    const response = await request(app).get('/users?page=2&limit=10');
    expect(response.body.data.length).toBeLessThanOrEqual(10);
    expect(response.body.pagination.page).toBe(2);
  });

  it('returns empty data for page beyond results', async () => {
    const response = await request(app).get('/users?page=100');
    expect(response.status).toBe(200);
    expect(response.body.data).toHaveLength(0);
    expect(response.body.pagination.hasMore).toBe(false);
  });

  it('rejects invalid page number', async () => {
    const response = await request(app).get('/users?page=-1');
    expect(response.status).toBe(400);
  });

  it('rejects page size exceeding maximum', async () => {
    const response = await request(app).get('/users?limit=1000');
    expect(response.status).toBe(400);
  });
});
```

### Filtering and Sorting

```typescript
describe('GET /users filtering', () => {
  it('filters by role', async () => {
    const response = await request(app).get('/users?role=admin');
    expect(response.body.data.every(u => u.role === 'admin')).toBe(true);
  });

  it('sorts by name ascending', async () => {
    const response = await request(app).get('/users?sort=name&order=asc');
    const names = response.body.data.map(u => u.name);
    expect(names).toEqual([...names].sort());
  });

  it('sorts by created date descending', async () => {
    const response = await request(app).get('/users?sort=createdAt&order=desc');
    const dates = response.body.data.map(u => new Date(u.createdAt).getTime());
    expect(dates).toEqual([...dates].sort((a, b) => b - a));
  });

  it('rejects invalid sort field', async () => {
    const response = await request(app).get('/users?sort=password');
    expect(response.status).toBe(400);
  });
});
```

### Authorization

```typescript
describe('Authorization', () => {
  it('returns 401 for unauthenticated requests', async () => {
    const response = await request(app).get('/users');
    expect(response.status).toBe(401);
  });

  it('returns 403 when user lacks required role', async () => {
    const response = await request(app)
      .delete('/users/123')
      .set('Authorization', `Bearer ${memberToken}`); // member, not admin

    expect(response.status).toBe(403);
  });

  it('allows admin to delete users', async () => {
    const response = await request(app)
      .delete(`/users/${testUser.id}`)
      .set('Authorization', `Bearer ${adminToken}`);

    expect(response.status).toBe(204);
  });
});
```

### Rate Limiting

```typescript
describe('Rate limiting', () => {
  it('returns 429 after exceeding rate limit', async () => {
    // Send requests up to the limit
    const requests = Array.from({ length: 101 }, () =>
      request(app).get('/users').set('Authorization', `Bearer ${token}`)
    );

    const responses = await Promise.all(requests);
    const tooMany = responses.filter(r => r.status === 429);
    expect(tooMany.length).toBeGreaterThan(0);
  });

  it('includes Retry-After header in 429 response', async () => {
    // ... trigger rate limit
    expect(response.headers['retry-after']).toBeDefined();
  });
});
```

### Malformed Requests

```typescript
describe('Malformed requests', () => {
  it('returns 400 for invalid JSON body', async () => {
    const response = await request(app)
      .post('/users')
      .set('Content-Type', 'application/json')
      .send('{ invalid json');

    expect(response.status).toBe(400);
  });

  it('returns 400 for wrong content type', async () => {
    const response = await request(app)
      .post('/users')
      .set('Content-Type', 'text/plain')
      .send('name=test');

    expect(response.status).toBe(400);
  });

  it('handles extremely large request body gracefully', async () => {
    const response = await request(app)
      .post('/users')
      .send({ name: 'a'.repeat(1_000_000) });

    expect(response.status).toBe(400);
  });
});
```

### Timeout Handling

```typescript
describe('Timeout handling', () => {
  it('returns 504 when downstream service times out', async () => {
    // Mock external service to delay beyond timeout
    nock('https://external-api.example.com')
      .get('/data')
      .delay(10000)
      .reply(200);

    const response = await request(app).get('/proxy/data');
    expect(response.status).toBe(504);
  });
});
```

## Python (pytest + httpx/TestClient)

```python
def test_list_users_returns_paginated_results(client, seed_users):
    response = client.get("/users?page=1&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 10
    assert data["total"] == len(seed_users)
    assert data["page"] == 1

def test_create_user_rejects_invalid_email(client):
    response = client.post("/users", json={"name": "Test", "email": "invalid"})

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(e["loc"] == ["body", "email"] for e in errors)
```
