Use before marking any browser-facing TypeScript UI change done — validates the change in a real browser session.

## Browser Validation Workflow

**Recommended tool: Playwright** — check `package.json` for `@playwright/test` or `playwright`.

### When to validate

- Any change that touches a component, page, route, or CSS
- Any change that affects data displayed in the UI
- After all unit tests pass and before setting a task to done

### Commands (Playwright)

```bash
# Run all UI tests
npx playwright test

# Run tests for a specific page/component
npx playwright test tests/e2e/foo.spec.ts

# Run headed (see the browser)
npx playwright test --headed

# Capture a screenshot of a specific URL
npx playwright screenshot --browser chromium http://localhost:3000/page --path .harness/screenshots/$(date +%s).png

# Show trace for a failed test
npx playwright show-trace test-results/trace.zip
```

### Without Playwright (raw CDP)

If Playwright is not configured, connect directly to Chrome's remote debugging port:

```bash
# Start Chrome with remote debugging
google-chrome --remote-debugging-port=9222 --headless --disable-gpu http://localhost:3000

# List open targets
curl http://localhost:9222/json

# Use the webSocketDebuggerUrl from the response to connect via CDP client
```

### Validation checklist before marking done

- [ ] Application starts without errors (`<see doc/spec/tech/browser-testing.md for boot command>`)
- [ ] Changed page/component renders without console errors
- [ ] UI tests pass (`npx playwright test`)
- [ ] Screenshot captured if making visual changes
