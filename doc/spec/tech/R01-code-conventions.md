---
title: Code Conventions
status: active
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# Code Conventions

**Scope:** Project-specific coding patterns, naming rules, and structural conventions that agents must follow when writing or modifying code in this project.

**What belongs here:** Concrete, project-specific rules about naming, file organisation, API patterns, and idioms that are not captured in the general engineering rules injected by harness-install.

**What does NOT belong here:**
- General language best practices → already injected into CLAUDE.md by harness-install
- Architectural layer boundaries → `doc/spec/tech/R00-system-architecture.md`
- Golden principles and agent retrospective rules → `doc/spec/tech/R02-golden-principles.md`

**How to use:** Read when writing new code or reviewing existing code for consistency. Update this file when a new convention is agreed upon.

---

## Naming Conventions

<!-- Add project-specific naming rules here. Examples:                          -->
<!-- - Files: kebab-case for modules, PascalCase for components                 -->
<!-- - Variables: camelCase for locals, UPPER_SNAKE for module-level constants  -->
<!-- - Functions: verb_noun pattern (e.g. get_user, create_order)               -->

## File and Directory Structure

<!-- Add structural rules here. Examples:                                        -->
<!-- - Where new services/modules go                                             -->
<!-- - Co-location rules (tests next to source vs. top-level tests/)            -->
<!-- - Index file conventions                                                    -->

## API and Interface Patterns

<!-- Add patterns for public interfaces. Examples:                               -->
<!-- - Return shapes (always { status, data } vs. plain values)                  -->
<!-- - Error handling conventions (exceptions vs. result types)                  -->
<!-- - Async patterns (async/await vs. callbacks vs. promises)                   -->

## Testing Conventions

<!-- Add project-specific test rules. Examples:                                  -->
<!-- - Test file naming (test_foo.py vs. foo.test.ts vs. FooTest.java)           -->
<!-- - Fixture and factory patterns                                               -->
<!-- - What to mock vs. what to use real implementations for                     -->

---

<!-- Add more sections as your project develops its conventions.                 -->
