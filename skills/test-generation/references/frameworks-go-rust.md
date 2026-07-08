# Go and Rust Testing

## Go Testing

### Test Structure

```go
package discount

import "testing"

func TestCalculateDiscount_GoldTier(t *testing.T) {
    // Arrange
    price := 100.0
    tier := TierGold

    // Act
    got := CalculateDiscount(price, tier)

    // Assert
    want := 20.0
    if got != want {
        t.Errorf("CalculateDiscount(%v, %v) = %v, want %v", price, tier, got, want)
    }
}
```

### Table-Driven Tests

The standard Go pattern for testing multiple cases. Every test with more than one case should use this pattern:

```go
func TestCalculateDiscount(t *testing.T) {
    tests := []struct {
        name     string
        price    float64
        tier     Tier
        want     float64
        wantErr  bool
    }{
        {
            name:  "gold tier applies 20% discount",
            price: 100.0,
            tier:  TierGold,
            want:  20.0,
        },
        {
            name:  "silver tier applies 10% discount",
            price: 100.0,
            tier:  TierSilver,
            want:  10.0,
        },
        {
            name:  "zero price returns zero discount",
            price: 0,
            tier:  TierGold,
            want:  0,
        },
        {
            name:    "invalid tier returns error",
            price:   100.0,
            tier:    Tier("platinum"),
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := CalculateDiscount(tt.price, tt.tier)

            if tt.wantErr {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if got != tt.want {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}
```

### Subtests with t.Run

```go
func TestUserService(t *testing.T) {
    t.Run("Create", func(t *testing.T) {
        t.Run("valid input saves user", func(t *testing.T) {
            // ...
        })
        t.Run("duplicate email returns error", func(t *testing.T) {
            // ...
        })
    })

    t.Run("Delete", func(t *testing.T) {
        t.Run("existing user removes from database", func(t *testing.T) {
            // ...
        })
    })
}
```

### Parallel Tests

```go
func TestExpensiveOperation(t *testing.T) {
    tests := []struct{ name string; input int; want int }{
        {"small input", 1, 1},
        {"large input", 1000, 500},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // Run this subtest in parallel

            got := ExpensiveOperation(tt.input)
            if got != tt.want {
                t.Errorf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

**Parallel safety**: When using `t.Parallel()`, ensure the loop variable is captured correctly (Go 1.22+ handles this automatically; for earlier versions, shadow the variable).

### Test Helpers

```go
// t.Helper() marks a function as a test helper — errors report the caller's line
func assertStatusCode(t *testing.T, got, want int) {
    t.Helper()
    if got != want {
        t.Errorf("status code = %d, want %d", got, want)
    }
}

// t.TempDir() provides an auto-cleaned temporary directory
func TestWriteConfig(t *testing.T) {
    dir := t.TempDir()
    path := filepath.Join(dir, "config.json")

    err := WriteConfig(path, defaultConfig)
    if err != nil {
        t.Fatal(err)
    }

    data, _ := os.ReadFile(path)
    // assert contents...
}
```

### HTTP Testing

```go
import (
    "net/http"
    "net/http/httptest"
    "testing"
)

func TestHealthEndpoint(t *testing.T) {
    // Arrange
    handler := NewRouter()
    req := httptest.NewRequest("GET", "/health", nil)
    w := httptest.NewRecorder()

    // Act
    handler.ServeHTTP(w, req)

    // Assert
    if w.Code != http.StatusOK {
        t.Errorf("status = %d, want %d", w.Code, http.StatusOK)
    }
}
```

### Error Testing

```go
// Test specific error types
func TestParse_InvalidInput(t *testing.T) {
    _, err := Parse("invalid")
    if err == nil {
        t.Fatal("expected error")
    }

    var parseErr *ParseError
    if !errors.As(err, &parseErr) {
        t.Fatalf("expected ParseError, got %T", err)
    }
    if parseErr.Line != 1 {
        t.Errorf("error line = %d, want 1", parseErr.Line)
    }
}
```

## Rust Testing (cargo test)

### Test Structure

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn gold_tier_applies_twenty_percent_discount() {
        // Arrange
        let price = 100.0;
        let tier = Tier::Gold;

        // Act
        let discount = calculate_discount(price, tier);

        // Assert
        assert_eq!(discount, 20.0);
    }

    #[test]
    fn zero_price_returns_zero_discount() {
        assert_eq!(calculate_discount(0.0, Tier::Gold), 0.0);
    }
}
```

### Assertions

```rust
assert_eq!(actual, expected);           // Equality
assert_ne!(actual, unexpected);         // Inequality
assert!(condition);                     // Boolean
assert!(result.is_ok());               // Result
assert!(result.is_err());

// With custom messages
assert_eq!(discount, 20.0, "Gold tier should give 20% of {}", price);
```

### Error Testing

```rust
#[test]
#[should_panic(expected = "invalid tier")]
fn invalid_tier_panics() {
    calculate_discount(100.0, Tier::try_from("platinum").unwrap());
}

// For Result-returning functions (preferred over panic)
#[test]
fn invalid_input_returns_error() {
    let result = parse_config("invalid");
    assert!(result.is_err());
    assert_eq!(
        result.unwrap_err().to_string(),
        "invalid configuration format"
    );
}
```

### Integration Tests

```rust
// tests/integration_test.rs — separate from unit tests
use my_crate::public_api;

#[test]
fn end_to_end_workflow() {
    let config = Config::default();
    let result = public_api::process(&config, "input data");
    assert!(result.is_ok());
}
```

### Property-Based Testing (proptest)

```rust
// Note: proptest is an optional dependency — mention in recommendations
use proptest::prelude::*;

proptest! {
    #[test]
    fn discount_never_exceeds_price(
        price in 0.0f64..1_000_000.0,
        tier in prop_oneof![Just(Tier::Bronze), Just(Tier::Silver), Just(Tier::Gold)]
    ) {
        let discount = calculate_discount(price, tier);
        prop_assert!(discount <= price, "discount {} exceeds price {}", discount, price);
        prop_assert!(discount >= 0.0, "discount should not be negative");
    }
}
```

**When to suggest property-based tests**: When the code has mathematical properties (commutativity, idempotency, invariants), range constraints, or serialization round-trips. Frame as a recommendation, not a default — property tests require the `proptest` crate.

### Test Organization

```
src/
  lib.rs          # Unit tests in #[cfg(test)] mod tests { ... }
  module.rs       # Unit tests inline
tests/
  integration.rs  # Integration tests (separate binary, only public API)
```

- **Unit tests**: Inside `#[cfg(test)]` blocks in the source file — can test private functions
- **Integration tests**: In `tests/` directory — can only test the public API
- **Doc tests**: In `///` comments — verify examples compile and run
