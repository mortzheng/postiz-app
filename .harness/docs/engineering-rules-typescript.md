## TypeScript Engineering Rules

### Invariants

- `"strict": true` in `tsconfig.json` — non-negotiable.
- Never use `any` — use `unknown` and narrow with type guards. `any` requires an explicit comment justifying it.
- Never use the non-null assertion operator (`!`) without a comment explaining why the value is guaranteed to exist.
- Use `interface` for object shapes, `type` for unions and mapped types.
- Use named exports only — no default exports.
- Always `await` promises — no floating promises.
- Use ESM (`"type": "module"` in `package.json`) — no mixing `require()` and `import`.
- Test with Vitest or Jest. Mock only at module boundaries (HTTP clients, databases) — not internal functions.
- Follow naming conventions: `PascalCase` types/classes, `camelCase` variables/functions, `SCREAMING_SNAKE_CASE` constants, `kebab-case` file names.

### Examples

**No `any` — use `unknown` and narrow**
```typescript
// WRONG — any disables all type checking downstream
function parse(input: any): any {
  return JSON.parse(input);
}

// CORRECT — unknown forces callers to narrow before use
function parse(input: string): unknown {
  return JSON.parse(input);
}

function parseUser(input: string): User {
  const data = parse(input);
  if (isUser(data)) return data;
  throw new Error("Invalid user data");
}
```

**`interface` for shapes, `type` for unions**
```typescript
// WRONG — type alias for a plain object shape (not extensible)
type UserProps = {
  name: string;
  email: string;
};

// CORRECT — interface for object shapes (extensible, mergeable)
interface UserProps {
  name: string;
  email: string;
}

// CORRECT — type for unions and mapped types
type Result = Success | Failure;
type Readonly<T> = { readonly [K in keyof T]: T[K] };
```

**Null handling — optional chaining and nullish coalescing**
```typescript
// WRONG — non-null assertion hides potential runtime errors
function getUserName(user: User | null): string {
  return user!.name;
}

// CORRECT — explicit handling with optional chaining and fallback
function getUserName(user: User | null): string {
  return user?.name ?? "Anonymous";
}
```

**Named exports, no default exports**
```typescript
// WRONG — default export makes renaming implicit and refactoring harder
export default class UserService { /* ... */ }
// import UserService from "./user-service";  // name not enforced

// CORRECT — named export ties the import to the declaration name
export class UserService { /* ... */ }
// import { UserService } from "./user-service";  // name is explicit
```

**Async/await — no floating promises**
```typescript
// WRONG — floating promise; errors silently disappear
function init() {
  loadConfig();  // returns Promise but is not awaited
}

// CORRECT — await the promise or handle the error explicitly
async function init() {
  await loadConfig();
}

// ALSO CORRECT — if you intentionally fire-and-forget, handle the error
function init() {
  loadConfig().catch((err) => log.error("Config load failed", err));
}
```

**`toEqual` over `toBe` for objects**
```typescript
// WRONG — toBe fails on structurally equal but referentially different objects
expect(getUser()).toBe({ name: "Alice" });

// CORRECT — toEqual checks structural equality
expect(getUser()).toEqual({ name: "Alice" });
```

### Recommended Linter Rules

When these rules are active in the project, the corresponding invariants above are mechanically enforced:

| Invariant | Tool | Rule |
|---|---|---|
| No `any` | ESLint | `@typescript-eslint/no-explicit-any` |
| No `!` assertion | ESLint | `@typescript-eslint/no-non-null-assertion` |
| No floating promises | ESLint | `@typescript-eslint/no-floating-promises` |
| No default exports | ESLint | `import/no-default-export` |
| Strict null checks | tsconfig | `"strict": true` (includes `strictNullChecks`) |
| Named imports | ESLint | `import/prefer-named-export` |

Run before committing:
```bash
# Type check without emitting
tsc --noEmit

# Lint and test
npm run lint && npm test
```
