# CLAUDE.md

> Auto-loaded by Claude Code CLI.

---

## Project Overview

Desktop tool (PySide6) for editing JSON configuration files used by the Bunseki application.
Manages 4 schema files: holder_groups.json, valid_holders.json, valid_tests.json, valid_samples.json.
These files define code normalization rules for converting Lab-Aid data into bunseki.csv.

Same corporate environment as Bunseki: SharePoint sync, USERPROFILE-based path resolution.

---

## Tech Stack

| Item | Value |
|------|-------|
| Language | Python |
| UI Framework | PySide6 |
| Package Manager | pip + requirements.txt |

---

## Directory Structure

- `app/config.py` — Path resolution and settings management
- `app/core/` — Data access layer (JSON I/O)
- `app/services/` — Business logic (validation, CRUD)
- `app/ui/` — UI layer (widgets, editors, pages)
- Dependency flow: UI → Service → Core (one-way only)

---

## Coding Conventions

- Type hints required on all functions
- Google-style docstrings for public functions/classes
- snake_case for functions/files, PascalCase for classes
- No logic in UI files — delegate to services
- Formatter: black (line length: 100)

---

## Design Guidelines

- White-based theme (#f5f7fa background, #333333 text)
- Same look & feel as Bunseki application
- Tree + Editor integrated layout
