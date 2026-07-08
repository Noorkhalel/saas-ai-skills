# Python Testing: pytest and unittest

## pytest

### Test Structure

```python
class TestCalculateDiscount:
    """Tests for the calculate_discount function."""

    def test_gold_tier_applies_twenty_percent(self):
        # Arrange
        price = 100.0
        tier = "gold"

        # Act
        result = calculate_discount(price, tier)

        # Assert
        assert result == 20.0

    def test_zero_price_returns_zero_discount(self):
        assert calculate_discount(0, "gold") == 0
```

### Naming Convention

- Test files: `test_<module>.py` or `<module>_test.py`
- Test classes: `TestClassName` (no need to inherit from anything)
- Test functions: `test_<behavior_description>` — descriptive enough to understand without reading the body
- Use plain `assert` — pytest rewrites assertions to show detailed diffs

### Fixtures

```python
import pytest

@pytest.fixture
def db_session():
    """Create a test database session with rollback isolation."""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user(db_session):
    """Insert a standard test user and return it."""
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.flush()
    return user

def test_user_can_update_email(db_session, sample_user):
    sample_user.email = "new@example.com"
    db_session.flush()

    refreshed = db_session.get(User, sample_user.id)
    assert refreshed.email == "new@example.com"
```

**Fixture scope**:
- `scope="function"` (default): Fresh fixture per test — use for mutable state
- `scope="class"`: Shared across tests in a class — use for read-only resources
- `scope="module"`: Shared across a file — use for expensive setup (e.g., database creation)
- `scope="session"`: Shared across entire test run — use for global resources (e.g., test server)

### Parametrize

```python
@pytest.mark.parametrize("tier,expected_rate", [
    ("bronze", 0.05),
    ("silver", 0.10),
    ("gold", 0.20),
])
def test_discount_rate_by_tier(tier, expected_rate):
    result = calculate_discount(100, tier)
    assert result == pytest.approx(100 * expected_rate)

# Parametrize with IDs for readable output
@pytest.mark.parametrize("input_val,expected", [
    pytest.param("", [], id="empty-string-returns-empty-list"),
    pytest.param("a,b,c", ["a", "b", "c"], id="comma-separated-splits-correctly"),
    pytest.param("a,,b", ["a", "", "b"], id="consecutive-delimiters-produce-empty-strings"),
])
def test_parse_csv(input_val, expected):
    assert parse_csv(input_val) == expected
```

### tmp_path (Built-in File Testing)

```python
def test_writes_report_to_file(tmp_path):
    output_file = tmp_path / "report.json"

    generate_report(output_path=output_file)

    content = json.loads(output_file.read_text())
    assert content["status"] == "complete"
    assert "timestamp" in content
```

### FastAPI / Starlette TestClient

```python
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user_returns_201(client):
    response = client.post("/users", json={
        "name": "Test User",
        "email": "test@example.com",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert "id" in data

def test_create_user_rejects_duplicate_email(client, sample_user):
    response = client.post("/users", json={
        "name": "Another User",
        "email": sample_user.email,  # duplicate
    })
    assert response.status_code == 409
```

### httpx AsyncClient (for async FastAPI)

```python
import httpx
import pytest

@pytest.fixture
async def async_client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.anyio
async def test_async_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
```

### Mocking

```python
from unittest.mock import patch, MagicMock, AsyncMock

def test_sends_welcome_email_on_registration(db_session):
    with patch("app.services.email.send_email") as mock_send:
        register_user(db_session, "new@example.com", "password")

        mock_send.assert_called_once_with(
            to="new@example.com",
            template="welcome",
        )

# Async mock
@pytest.mark.anyio
async def test_fetches_remote_config():
    with patch("app.config.fetch_remote", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"feature_flag": True}
        config = await load_config()
        assert config["feature_flag"] is True
```

### Exception Testing

```python
def test_invalid_tier_raises_value_error():
    with pytest.raises(ValueError, match="Unknown tier: 'platinum'"):
        calculate_discount(100, "platinum")
```

## unittest

For codebases that use `unittest` (Django default, older Python projects):

```python
import unittest

class TestCalculateDiscount(unittest.TestCase):
    def setUp(self):
        self.calculator = DiscountCalculator()

    def test_gold_tier_applies_twenty_percent(self):
        result = self.calculator.calculate(100, "gold")
        self.assertEqual(result, 20.0)

    def test_invalid_tier_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate(100, "platinum")

    def test_discount_is_close_for_floating_point(self):
        result = self.calculator.calculate(19.99, "silver")
        self.assertAlmostEqual(result, 1.999, places=2)
```

**Key differences from pytest**:
- Must inherit from `unittest.TestCase`
- Uses `self.assertEqual()` / `self.assertRaises()` instead of plain `assert`
- `setUp()` / `tearDown()` instead of fixtures
- Less readable output, fewer built-in features
- When in doubt and the project doesn't mandate unittest, prefer pytest
