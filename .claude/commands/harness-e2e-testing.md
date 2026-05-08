Use when writing or running integration/e2e tests in TypeScript — defines directory conventions, test commands, and isolation rules.

## Integration & E2E Testing Guide (TypeScript)

### Directory conventions

Place integration and end-to-end tests in these directories:

```
tests/
├── integration/     # Tests that hit real databases, APIs, or services
└── e2e/             # Playwright/Cypress end-to-end tests
e2e/                 # Alternative: top-level e2e directory
```

The completion gate automatically detects and runs e2e tests when test files exist (`*.test.ts`, `*.spec.ts`).

### Playwright setup

```bash
# Install Playwright
npm init playwright@latest

# Run all e2e tests
npx playwright test

# Run a specific test
npx playwright test tests/e2e/login.spec.ts

# Run headed (see the browser)
npx playwright test --headed

# Show HTML report
npx playwright show-report
```

### Playwright test patterns

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('login page loads', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('heading')).toContainText('Sign In');
});

test('successful login redirects to dashboard', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'user@example.com');
  await page.fill('[name="password"]', 'password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

### Cypress setup

```bash
# Install Cypress
npm install --save-dev cypress

# Open Cypress UI
npx cypress open

# Run headless
npx cypress run
```

### Integration test patterns

For API integration tests using vitest/jest:

```typescript
// tests/integration/api.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

let server: TestServer;

beforeAll(async () => {
  server = await startTestServer();
});

afterAll(async () => {
  await server.close();
});

it('creates a user', async () => {
  const res = await fetch(`${server.url}/api/users`, {
    method: 'POST',
    body: JSON.stringify({ name: 'Test' }),
  });
  expect(res.status).toBe(201);
});
```
