# Database Testing

## Core Principles

1. **Each test gets clean state** — never rely on data from previous tests
2. **Use transactions for isolation** — rollback is faster than truncate + seed
3. **Test constraints at the database level** — don't just trust application validation
4. **Use realistic data shapes** — but minimal; don't seed 10,000 rows for a unit test

## Isolation Strategies

### Transaction Rollback (Fastest)

Wrap each test in a transaction and roll back after:

```python
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

```typescript
// TypeORM / Knex pattern
beforeEach(async () => {
  await db.raw('BEGIN');
});

afterEach(async () => {
  await db.raw('ROLLBACK');
});
```

### Truncate + Seed (When Transactions Don't Work)

For multi-connection tests (e.g., testing concurrent access):

```python
@pytest.fixture(autouse=True)
def clean_db(db_session):
    yield
    for table in reversed(metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
```

### Containerized Database (Most Realistic)

Using TestContainers or pg_tmp for a real database per suite:

```python
@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:15") as pg:
        yield pg.get_connection_url()
```

## Test Categories

### CRUD Operations

```python
class TestUserRepository:
    def test_create_persists_user(self, repo, db_session):
        user = repo.create(name="Alice", email="alice@example.com")

        found = db_session.query(User).filter_by(id=user.id).one()
        assert found.name == "Alice"
        assert found.email == "alice@example.com"

    def test_update_changes_fields(self, repo, sample_user):
        repo.update(sample_user.id, name="Updated")

        refreshed = repo.find_by_id(sample_user.id)
        assert refreshed.name == "Updated"

    def test_delete_removes_user(self, repo, sample_user):
        repo.delete(sample_user.id)

        assert repo.find_by_id(sample_user.id) is None
```

### Transactions

```python
def test_transfer_is_atomic(self, repo, alice, bob):
    """If transfer fails mid-way, neither account should change."""
    original_alice = alice.balance
    original_bob = bob.balance

    with pytest.raises(InsufficientFundsError):
        repo.transfer(alice.id, bob.id, amount=999999)

    refreshed_alice = repo.find_by_id(alice.id)
    refreshed_bob = repo.find_by_id(bob.id)
    assert refreshed_alice.balance == original_alice
    assert refreshed_bob.balance == original_bob
```

### Constraints

```python
def test_unique_email_constraint(self, repo, sample_user):
    """Database enforces uniqueness even if app validation is bypassed."""
    with pytest.raises(IntegrityError):
        repo.create(name="Other", email=sample_user.email)

def test_not_null_constraint(self, repo):
    with pytest.raises(IntegrityError):
        repo.create(name=None, email="test@example.com")

def test_foreign_key_prevents_orphan(self, db_session):
    """Cannot create an order referencing a nonexistent user."""
    with pytest.raises(IntegrityError):
        db_session.execute(
            insert(orders).values(user_id="nonexistent", total=100)
        )
```

### Migrations

```python
def test_migration_adds_column(self, engine):
    """After migration 003, users table has 'role' column."""
    run_migrations(engine, target="003")

    inspector = inspect(engine)
    columns = {c['name'] for c in inspector.get_columns('users')}
    assert 'role' in columns

def test_migration_is_reversible(self, engine):
    """Migration 003 can be rolled back without data loss."""
    run_migrations(engine, target="003")
    rollback_migration(engine, target="002")

    inspector = inspect(engine)
    columns = {c['name'] for c in inspector.get_columns('users')}
    assert 'role' not in columns
```

### Indexes and Query Performance

```python
def test_email_index_exists(self, engine):
    inspector = inspect(engine)
    indexes = inspector.get_indexes('users')
    email_indexes = [i for i in indexes if 'email' in i['column_names']]
    assert len(email_indexes) > 0

def test_query_uses_index(self, db_session, seed_1000_users):
    """Verify the query plan uses the email index."""
    result = db_session.execute(
        text("EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com'")
    )
    plan = result.scalar()
    assert 'Index Scan' in plan or 'Index Only Scan' in plan
```

### Optimistic Locking

```python
def test_concurrent_update_detects_conflict(self, repo, sample_user):
    """Second update with stale version should fail."""
    # Simulate two concurrent reads
    user_v1 = repo.find_by_id(sample_user.id)
    user_v2 = repo.find_by_id(sample_user.id)

    # First update succeeds
    repo.update(user_v1.id, name="First", version=user_v1.version)

    # Second update should fail (stale version)
    with pytest.raises(OptimisticLockError):
        repo.update(user_v2.id, name="Second", version=user_v2.version)
```

### Rollback Behavior

```python
def test_failed_operation_rolls_back_all_changes(self, repo, db_session):
    initial_count = db_session.query(User).count()

    with pytest.raises(Exception):
        repo.batch_create([
            {"name": "Valid", "email": "valid@test.com"},
            {"name": None, "email": None},  # Will fail
        ])

    assert db_session.query(User).count() == initial_count
```

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Shared test data across tests | Order-dependent failures | Each test creates its own data |
| Testing with production database | Data corruption, slow | Use test database with isolation |
| Not testing constraints | App bypasses allow invalid data | Test at the SQL level directly |
| Seeding too much data | Slow tests, unclear intent | Minimal data per test |
| Not cleaning up after tests | State leaks between tests | Transaction rollback or truncate |
