"""
Spec index generator — scans doc/spec/product/ and doc/spec/tech/, reads
title from YAML frontmatter, and injects a ``spec-index`` section into
CLAUDE.md.

Invoked as a function (``main(target_dir)``) from the completion gate
(``verify_completion.py`` and ``check_completion.py``) and from the
``harness-install index`` CLI subcommand. Running this module directly
regenerates the index against the resolved target directory.
"""
import os
import re
import sys
from pathlib import Path

_DEFAULT_TARGET_DIR = Path(__file__).parent.parent.parent
_TARGET_DIR = (
    Path(os.environ["HARNESS_REPO_ROOT"])
    if "HARNESS_REPO_ROOT" in os.environ
    else _DEFAULT_TARGET_DIR
)

MARKER_BEGIN = "<!-- harness-scaffold: begin {section} -->"
MARKER_END = "<!-- harness-scaffold: end {section} -->"
SPEC_INDEX_SECTION = "spec-index"


def _extract_title(path: Path) -> str | None:
    """Extract title: value from YAML frontmatter, or None if absent."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None
    frontmatter = m.group(1)
    title_match = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
    if not title_match:
        return None
    return title_match.group(1).strip()


def _build_index(target_dir: Path) -> str:
    """Return the spec index markdown content (without markers)."""
    sections = ["## Spec Index\n"]

    for subdir, heading in [
        ("doc/spec/product", "### Product Specs (`doc/spec/product/`)"),
        ("doc/spec/tech", "### Tech Specs (`doc/spec/tech/`)"),
    ]:
        spec_dir = target_dir / subdir
        sections.append(heading)

        spec_files: list[Path] = []
        if spec_dir.exists():
            spec_files = sorted(
                f for f in spec_dir.glob("*.md") if f.name != "README.md"
            )

        if not spec_files:
            sections.append("_(no specs yet)_\n")
            continue

        for spec_file in spec_files:
            title = _extract_title(spec_file)
            if title is None:
                print(
                    f"[spec-index] warning: {spec_file.relative_to(target_dir)} "
                    f"has no title: in frontmatter; using filename",
                    file=sys.stderr,
                )
                title = spec_file.stem
            rel = spec_file.relative_to(target_dir)
            sections.append(f"- [{spec_file.name}]({rel}) — {title}")

        sections.append("")

    return "\n".join(sections)


def _inject_section(content: str, section_content: str) -> str:
    """Inject or replace the spec-index marker block in CLAUDE.md content."""
    begin_marker = MARKER_BEGIN.format(section=SPEC_INDEX_SECTION)
    end_marker = MARKER_END.format(section=SPEC_INDEX_SECTION)

    block = f"{begin_marker}\n{section_content.strip()}\n{end_marker}\n"

    pattern = re.escape(begin_marker) + r".*?" + re.escape(end_marker)
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, block.strip(), content, flags=re.DOTALL)
    else:
        if not content.endswith("\n\n"):
            content = content.rstrip() + "\n\n"
        content += block

    return content


def main(target_dir: Path | None = None) -> None:
    """Regenerate the spec index and inject it into CLAUDE.md and AGENTS.md.

    Each file is updated only if it exists; missing files are silently skipped.
    """
    if target_dir is None:
        target_dir = _TARGET_DIR

    targets = [target_dir / "CLAUDE.md", target_dir / "AGENTS.md"]
    if not any(p.exists() for p in targets):
        return

    index_content = _build_index(target_dir)
    for path in targets:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        content = _inject_section(content, index_content)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
