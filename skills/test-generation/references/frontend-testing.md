# Frontend Testing: React, Next.js, Vue, Angular

## Core Principle

Test from the user's perspective. Users don't know about component state, props, or hooks — they see text, buttons, forms, and loading spinners. Your tests should interact with what users see.

## React / Next.js (Testing Library)

### Component Rendering

```typescript
import { render, screen } from '@testing-library/react';

it('displays user name after loading', async () => {
  render(<UserProfile userId="123" />);

  // Wait for async data to load
  const heading = await screen.findByRole('heading', { name: 'Jane Doe' });
  expect(heading).toBeInTheDocument();
});

it('shows loading spinner initially', () => {
  render(<UserProfile userId="123" />);

  expect(screen.getByRole('progressbar')).toBeInTheDocument();
});

it('shows error message when fetch fails', async () => {
  server.use(
    rest.get('/api/users/123', (req, res, ctx) =>
      res(ctx.status(500))
    )
  );

  render(<UserProfile userId="123" />);

  expect(await screen.findByRole('alert')).toHaveTextContent(
    'Failed to load user'
  );
});
```

### State Updates

```typescript
it('increments counter when button is clicked', async () => {
  const user = userEvent.setup();
  render(<Counter initialCount={0} />);

  await user.click(screen.getByRole('button', { name: 'Increment' }));

  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

### User Interactions

```typescript
import userEvent from '@testing-library/user-event';

it('submits form with entered data', async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<ContactForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText('Name'), 'John Doe');
  await user.type(screen.getByLabelText('Email'), 'john@example.com');
  await user.selectOptions(screen.getByLabelText('Subject'), 'support');
  await user.click(screen.getByRole('button', { name: 'Send' }));

  expect(onSubmit).toHaveBeenCalledWith({
    name: 'John Doe',
    email: 'john@example.com',
    subject: 'support',
  });
});
```

### Accessibility Testing

```typescript
it('form fields have accessible labels', () => {
  render(<RegistrationForm />);

  // These queries will fail if labels are missing — accessibility by default
  expect(screen.getByLabelText('Email address')).toBeInTheDocument();
  expect(screen.getByLabelText('Password')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Create Account' })).toBeEnabled();
});

it('error messages are associated with form fields', async () => {
  const user = userEvent.setup();
  render(<RegistrationForm />);

  await user.click(screen.getByRole('button', { name: 'Create Account' }));

  // aria-describedby links error to field
  const emailInput = screen.getByLabelText('Email address');
  expect(emailInput).toHaveAccessibleDescription('Email is required');
});
```

### Loading and Error States

```typescript
it('shows skeleton loader while data loads', () => {
  render(<DataTable loading={true} />);

  expect(screen.getByTestId('skeleton-loader')).toBeInTheDocument();
  expect(screen.queryByRole('table')).not.toBeInTheDocument();
});

it('shows empty state when no results', () => {
  render(<DataTable data={[]} />);

  expect(screen.getByText('No results found')).toBeInTheDocument();
});

it('shows retry button on error', async () => {
  const user = userEvent.setup();
  const onRetry = vi.fn();
  render(<DataTable error="Network error" onRetry={onRetry} />);

  expect(screen.getByRole('alert')).toHaveTextContent('Network error');

  await user.click(screen.getByRole('button', { name: 'Retry' }));
  expect(onRetry).toHaveBeenCalled();
});
```

### Navigation

```typescript
import { MemoryRouter } from 'react-router-dom';

it('navigates to user profile on row click', async () => {
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={['/users']}>
      <App />
    </MemoryRouter>
  );

  await user.click(screen.getByText('Jane Doe'));

  expect(await screen.findByRole('heading', { name: 'Jane Doe' })).toBeInTheDocument();
});
```

## Vue (Vue Testing Library or Vitest)

```typescript
import { render, screen } from '@testing-library/vue';
import userEvent from '@testing-library/user-event';

it('emits submit event with form data', async () => {
  const user = userEvent.setup();
  const { emitted } = render(ContactForm);

  await user.type(screen.getByLabelText('Name'), 'John');
  await user.click(screen.getByRole('button', { name: 'Submit' }));

  expect(emitted().submit[0]).toEqual([{ name: 'John' }]);
});
```

## Angular (Angular Testing Library)

```typescript
import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';

it('displays filtered results', async () => {
  const user = userEvent.setup();
  await render(UserListComponent, {
    providers: [{ provide: UserService, useValue: mockUserService }],
  });

  await user.type(screen.getByLabelText('Search'), 'admin');

  expect(screen.getByText('Admin User')).toBeInTheDocument();
  expect(screen.queryByText('Regular User')).not.toBeInTheDocument();
});
```

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `container.querySelector('.btn')` | Tests implementation (CSS class) | `screen.getByRole('button', { name: '...' })` |
| Asserting on component state/props | Tests internals, not behavior | Assert on rendered output |
| Manual `act()` wrapping | Indicates wrong query usage | Use `findBy*` queries or `userEvent` |
| `fireEvent.change` for typing | Doesn't simulate real user behavior | Use `userEvent.type()` |
| Testing library internals (hooks) | Couples to implementation | Test the component that uses the hook |
| Snapshot of entire component | Brittle, unclear what matters | Assert specific elements and text |
