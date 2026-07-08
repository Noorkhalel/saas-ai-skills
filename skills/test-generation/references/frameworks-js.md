# JavaScript/TypeScript Testing: Jest, Vitest, Testing Library

## Jest

### Test Structure

```typescript
describe('ModuleName', () => {
  describe('methodName', () => {
    it('returns expected result when given valid input', () => {
      // Arrange
      const input = createValidInput();

      // Act
      const result = moduleName.methodName(input);

      // Assert
      expect(result).toBe(expectedValue);
    });
  });
});
```

### Naming Convention

Use `describe` for the module/class, nested `describe` for the method, and `it` for the specific behavior:
- `it('returns 0 when price is negative')` — behavior-based
- `it('throws InvalidInputError for missing required fields')` — error behavior
- NOT: `it('should work correctly')` — meaningless

### Setup and Teardown

```typescript
// Per-test setup (preferred — makes dependencies explicit)
beforeEach(() => {
  jest.clearAllMocks(); // Reset mock state between tests
});

// Per-suite setup (only for expensive, read-only resources)
beforeAll(async () => {
  db = await createTestDatabase();
});

afterAll(async () => {
  await db.close();
});
```

### Module Mocking

```typescript
// Mock an entire module
jest.mock('./emailService', () => ({
  sendEmail: jest.fn().mockResolvedValue({ sent: true }),
}));

// Mock a specific method
jest.spyOn(userService, 'findById').mockResolvedValue(testUser);

// Restore original implementation
afterEach(() => {
  jest.restoreAllMocks();
});
```

**Mock discipline**: Always call `jest.clearAllMocks()` or `jest.restoreAllMocks()` in `beforeEach`/`afterEach`. Leaked mock state between tests is a top source of flakiness.

### Async Testing

```typescript
// async/await (preferred)
it('fetches user data', async () => {
  const user = await userService.getUser('123');
  expect(user.name).toBe('Test User');
});

// Rejections
it('throws when user not found', async () => {
  await expect(userService.getUser('nonexistent'))
    .rejects.toThrow(NotFoundError);
});
```

### Fake Timers

```typescript
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

it('debounces search input by 300ms', () => {
  const onSearch = jest.fn();
  render(<SearchInput onSearch={onSearch} />);

  userEvent.type(screen.getByRole('searchbox'), 'query');
  expect(onSearch).not.toHaveBeenCalled();

  jest.advanceTimersByTime(300);
  expect(onSearch).toHaveBeenCalledWith('query');
});
```

### Snapshot Testing — Use Sparingly

Snapshots verify *structure*, not *behavior*. Use only for:
- Serialized output formats (JSON responses, config generation)
- Rendered component markup (when layout is the behavior)

**Never use snapshots for**: Logic verification, error messages, calculated values. These deserve explicit assertions that document intent.

```typescript
// Acceptable: Verifying a complex serialization format
it('serializes user profile to expected JSON shape', () => {
  expect(serializeProfile(testUser)).toMatchSnapshot();
});

// Not acceptable: Testing logic via snapshot
// it('calculates discount correctly', () => {
//   expect(calculateDiscount(100, 'gold')).toMatchSnapshot();
// });
// Use: expect(calculateDiscount(100, 'gold')).toBe(20);
```

## Vitest

Vitest is API-compatible with Jest. Key differences:

- **Imports**: `import { describe, it, expect, vi } from 'vitest'` (explicit imports, not globals)
- **Mock function**: `vi.fn()` instead of `jest.fn()`; `vi.spyOn()` instead of `jest.spyOn()`
- **Module mocking**: `vi.mock('./module')` instead of `jest.mock('./module')`
- **Timers**: `vi.useFakeTimers()` / `vi.useRealTimers()`
- **Config**: `vitest.config.ts` — typically extends `vite.config.ts`

```typescript
import { describe, it, expect, vi } from 'vitest';

describe('calculateDiscount', () => {
  it('applies gold tier rate', () => {
    expect(calculateDiscount(100, 'gold')).toBe(20);
  });
});
```

## Testing Library

Testing Library enforces testing from the user's perspective. Core principle: **test what users see and do, not implementation details**.

### Query Priority

Use queries in this order of preference:

1. `getByRole` — accessible role (button, textbox, heading) — **always prefer this**
2. `getByLabelText` — form field by its label
3. `getByPlaceholderText` — when no label exists
4. `getByText` — visible text content
5. `getByDisplayValue` — current value of form elements
6. `getByAltText` — images
7. `getByTitle` — title attribute
8. `getByTestId` — **last resort only**

**Never use**: `container.querySelector`, `container.innerHTML`, or direct DOM traversal. These test implementation, not behavior.

### Async Queries

```typescript
// For elements that appear asynchronously (after API calls, state updates)
const element = await screen.findByText('Loaded successfully');

// waitFor for complex conditions
await waitFor(() => {
  expect(screen.getByRole('list')).toHaveTextContent('Item 1');
});
```

### User Events

```typescript
import userEvent from '@testing-library/user-event';

it('submits the form with entered data', async () => {
  const user = userEvent.setup();
  render(<LoginForm onSubmit={mockSubmit} />);

  await user.type(screen.getByLabelText('Email'), 'user@example.com');
  await user.type(screen.getByLabelText('Password'), 'password123');
  await user.click(screen.getByRole('button', { name: 'Sign In' }));

  expect(mockSubmit).toHaveBeenCalledWith({
    email: 'user@example.com',
    password: 'password123',
  });
});
```

### Common Anti-Patterns

- ❌ `fireEvent.change(input, { target: { value: 'text' } })` — use `userEvent.type()` instead (simulates real typing)
- ❌ Wrapping in `act()` manually — `userEvent` and `findBy*` handle this
- ❌ `getByTestId('submit-btn')` — use `getByRole('button', { name: 'Submit' })`
- ❌ Asserting on component state/props — assert on rendered output
