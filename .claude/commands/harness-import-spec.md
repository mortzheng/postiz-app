Use when bringing external documents (Confluence, Google Docs, local files, pasted content) into `doc/spec/` for the first time, or when re-syncing updates from a previously imported source.

**Modes:**
- **Import** (default) — convert an external document into one or more spec files
- **Sync** — re-read previously imported sources and propose updates for changed documents

---

## Import Mode

When the user provides a source document, follow these steps:

### Step 1 — Determine the source type

Ask the user for the source. Supported types:

| Source type | How to read |
|---|---|
| **Confluence URL** | Extract the page ID from the URL, then use the `getConfluencePage` MCP tool to fetch content |
| **Google Doc** | Ask user to paste content or provide a local export (markdown, HTML, or PDF) |
| **Local file** | Read the file directly using the Read tool |
| **Pasted content** | Work with the content inline |

### Step 2 — Read the target spec schema

Read `.harness/specs/meta/spec-schemas.md` to understand the required structure for:
- **Product specs** (`doc/spec/product/`) — Overview, Behavior, or Data Schema specs
- **Tech specs** (`doc/spec/tech/`) — System Context or Container specs

### Step 3 — Classify the document

Analyze the source content and classify what specs it maps to:

- **Product spec only** — the document describes user-facing features, business rules, acceptance criteria, or behavioral requirements
- **Tech spec only** — the document describes architecture, components, data flow, technology choices, or system design
- **Both** — the document contains both product requirements and technical design → split into two separate specs

Tell the user your classification and get confirmation before proceeding.

### Step 4 — Auto-detect the next available prefix

For each target directory (`doc/spec/product/` or `doc/spec/tech/`):

1. List existing files in the directory
2. Find the highest `NN-` numeric prefix (e.g., if `03-mobile-platform-support.md` exists, highest is `03`)
3. Use `(highest + 1)` zero-padded to 2 digits as the new prefix

### Step 5 — Generate the spec(s)

For each spec to generate:

1. Create a filename: `NN-<slug>.md` where `<slug>` is a short kebab-case name derived from the document title
2. Write the file with:
   - Proper YAML frontmatter (`title`, `status: draft`, `created`, `updated`)
   - All required sections per the schema in `spec-schemas.md`
   - Content restructured from the source document to fit the schema sections
3. **Do not invent content** — only restructure what exists in the source. If a required section has no corresponding content in the source, add a `<!-- TODO: fill in from source -->` placeholder
4. Present the generated spec to the user for review before writing

### Step 6 — Update the import manifest

After the user approves, update `doc/spec/.import-manifest.json`:

```json
{
  "version": "1",
  "imports": [
    {
      "source_type": "confluence | gdoc | file | paste",
      "source_ref": "<URL or file path — empty string for paste>",
      "target_specs": ["doc/spec/product/NN-name.md"],
      "last_synced": "<ISO-8601 UTC timestamp>",
      "source_hash": "<sha256 of the source content at time of import>"
    }
  ]
}
```

If the manifest does not exist, create it. If it exists, append to the `imports` array.

### Step 7 — Update the spec index

After writing specs, remind the user to run `harness-install upgrade` (or manually update the spec index in CLAUDE.md) so the new specs appear in the index.

---

## Sync Mode

When the user asks to sync or update imported specs:

### Step 1 — Read the manifest

Read `doc/spec/.import-manifest.json`. If it does not exist, inform the user that no imports have been tracked and offer to run an import instead.

### Step 2 — Re-fetch each source

For each entry in the manifest:

1. Re-read the source document using the same method as the original import
2. Compute the SHA-256 hash of the current source content
3. Compare with `source_hash` in the manifest

### Step 3 — Report changes

Present a summary:

```
## Import Sync Report

### Unchanged
- doc/spec/product/03-payments.md ← confluence://12345 (no changes)

### Changed
- doc/spec/tech/04-api-design.md ← confluence://67890
  Source changed since 2026-04-01T10:00:00Z

### Unreachable
- doc/spec/product/05-notifications.md ← (paste — cannot re-fetch)
```

### Step 4 — Propose updates

For each **Changed** entry:

1. Re-run the import pipeline (classify → generate) against the new source content
2. Diff the generated spec against the current spec file
3. Present the diff to the user
4. On approval, update the spec file, `last_synced`, and `source_hash` in the manifest

**Important:** If the current spec has been manually edited since the last sync, warn the user and show both the manual edits and the source changes so they can merge intentionally.

### Step 5 — Handle unreachable sources

For paste-based imports (`source_type: "paste"`), sync cannot re-fetch the source. Report these as unreachable and suggest the user paste updated content for a fresh import.

---

## Rules

- **Never invent content.** Only restructure what exists in the source document.
- **Always show the generated spec for review** before writing to disk.
- **Preserve existing manual edits** — when syncing, warn if the spec has diverged from the last import.
- **One manifest per project** at `doc/spec/.import-manifest.json`.
- **Frontmatter status is always `draft`** for newly imported specs — the user promotes to `active` after review.
