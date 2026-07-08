# End-to-End Testing: Playwright and Cypress

## Playwright

### Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test('allows user to log in with valid credentials', async ({ page }) => {
    // Arrange
    await page.goto('/login');

    // Act
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('validPassword');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Assert
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });
});
```

### Resilient Selectors — Priority Order

1. **Role-based** (ARIA roles): `page.getByRole('button', { name: 'Submit' })` — **always prefer**
2. **Label-based**: `page.getByLabel('Email')` — for form fields
3. **Text-based**: `page.getByText('Welcome back')` — for visible content
4. **Placeholder**: `page.getByPlaceholder('Search...')` — when no label
5. **Test ID**: `page.getByTestId('checkout-form')` — **last resort only**

**Never use**: CSS selectors for styling classes (`.btn-primary`), XPath, or generated IDs. These break on UI changes that don't affect functionality.

### Web-First Assertions (Auto-Waiting)

Playwright assertions automatically wait and retry. Use them instead of manual waits:

```typescript
// GOOD: Auto-waits for element to be visible (up to timeout)
await expect(page.getByText('Success')).toBeVisible();
await expect(page.getByRole('alert')).toHaveText('Saved!');
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('Dashboard');

// BAD: Manual wait — flaky, arbitrary, slow
await page.waitForTimeout(3000); // NEVER do this
await page.waitForSelector('.success-message'); // Prefer web-first assertions
```

**Critical rule**: `page.waitForTimeout()` is NEVER acceptable in generated tests. If you need to wait for something, use a web-first assertion that waits for the specific condition.

### Authentication State Reuse

For tests that require a logged-in user, authenticate once and reuse the state:

```typescript
// global-setup.ts — runs once before all tests
import { chromium } from '@playwright/test';

async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('/login');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.context().storageState({ path: 'tests/.auth/user.json' });
  await browser.close();
}

export default globalSetup;
```

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /global-setup\.ts/ },
    {
      name: 'authenticated',
      dependencies: ['setup'],
      use: { storageState: 'tests/.auth/user.json' },
    },
  ],
});
```

### Test Isolation

Each test gets its own `BrowserContext` by default. Additional isolation:
- Use `test.describe.configure({ mode: 'serial' })` only when tests must share state (e.g., multi-step workflows)
- Prefer independent tests that set up their own state
- Use API calls to create test data instead of UI interactions (faster, more reliable)

### Network Interception

```typescript
// Mock API responses for controlled testing
await page.route('**/api/users', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Test User' }]),
  });
});

// Simulate network errors
await page.route('**/api/data', (route) => route.abort('connectionrefused'));
```

### Visual Regression (Optional)

```typescript
// Only when layout/appearance IS the behavior being tested
await expect(page).toHaveScreenshot('dashboard-loaded.png', {
  maxDiffPixels: 100,
});
```

## Cypress

### Test Structure

```typescript
describe('Login Flow', () => {
  it('allows user to log in with valid credentials', () => {
    // Arrange
    cy.visit('/login');

    // Act
    cy.findByLabelText('Email').type('user@example.com');
    cy.findByLabelText('Password').type('validPassword');
    cy.findByRole('button', { name: 'Sign In' }).click();

    // Assert
    cy.findByRole('heading', { name: 'Dashboard' }).should('be.visible');
    cy.url().should('include', '/dashboard');
  });
});
```

### Selector Strategy

Use `@testing-library/cypress` for consistent Testing Library queries:

```typescript
// GOOD: User-facing queries
cy.findByRole('button', { name: 'Submit' });
cy.findByLabelText('Email');
cy.findByText('Welcome');

// AVOID: Implementation-coupled selectors
cy.get('.btn-submit'); // CSS class — breaks on styling changes
cy.get('#email-input'); // ID — fragile
```

### Cypress Auto-Waiting

Cypress commands automatically retry assertions. Do not add explicit waits:

```typescript
// GOOD: Cypress retries until assertion passes or timeout
cy.findByText('Loading...').should('not.exist');
cy.findByRole('table').should('contain', 'Order #123');

// BAD: Arbitrary waits
cy.wait(5000); // NEVER
```

### API Interception

```typescript
cy.intercept('GET', '/api/users', {
  statusCode: 200,
  body: [{ id: 1, name: 'Test User' }],
}).as('getUsers');

cy.visit('/users');
cy.wait('@getUsers'); // Wait for specific request, not arbitrary time
cy.findByText('Test User').should('be.visible');
```

### Authentication

```typescript
// Custom command for programmatic login (faster than UI login)
Cypress.Commands.add('login', (email, password) => {
  cy.request('POST', '/api/auth/login', { email, password })
    .then(({ body }) => {
      window.localStorage.setItem('token', body.token);
    });
});

// Usage in tests
beforeEach(() => {
  cy.login('test@example.com', 'password');
});
```

## Common E2E Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Fixed waits (`waitForTimeout`, `cy.wait(ms)`) | Flaky: too short = failure, too long = slow | Use auto-waiting assertions |
| CSS class selectors | Break on styling changes | Use role/label/text selectors |
| Testing through UI what can be tested via API | Slow, flaky | Reserve E2E for full user flows only |
| Shared state between tests | Order-dependent failures | Each test creates its own state |
| Testing implementation details | Breaks on refactor | Test user-observable behavior |
| Hardcoded URLs/ports | Breaks across environments | Use config/environment variables |
