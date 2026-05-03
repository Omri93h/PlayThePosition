# Codex Prompt Templates

Reusable prompt shapes for Play The Position. Keep prompts short, replace placeholders, and do not execute before a PLAN is approved.

## PLAN Prompt

```text
Read only:
- AGENTS.md
- docs/product/ASSISTANT_WORKFLOW.md
- current_focus.md
- docs/product/PROGRESS.md
- docs/product/DECISIONS.md
- relevant docs/files only as needed

Task:
Plan BLOCK / FEATURE.

Goal:
GOAL

Scope:
- Plan only.
- Do not edit files.
- Do not implement.
- Do not expand beyond FEATURE.

Output exactly:
1. Current status
2. Proposed scope
3. Files expected to change
4. Tests/checks to add or update
5. Risks / blockers
6. Checks to run
7. Stop and wait for approval
```

## EXECUTE Prompt

```text
Implement the approved plan for BLOCK / FEATURE.

Read only first:
- AGENTS.md
- docs/product/ASSISTANT_WORKFLOW.md
- current_focus.md
- docs/product/PROGRESS.md
- relevant docs/files only as needed

Approved scope:
- GOAL
- FILES / AREAS

Strictly do NOT:
- OUT_OF_SCOPE_ITEMS

Run checks:
- CHECKS
- git diff --check
- git status --short

Output:
1. Changed files
2. Exact summary
3. Check results
4. Self-review against scope
5. git status --short
6. Suggested commit message

Stop after implementation and checks.
```

## FIX Prompt

```text
Fix the current uncommitted BLOCK / FEATURE only.

Read only first:
- AGENTS.md
- docs/product/ASSISTANT_WORKFLOW.md
- current_focus.md
- relevant files only as needed

Fix:
- ISSUE

Rules:
- Do not add features.
- Do not touch unrelated files.
- Keep this inside the current uncommitted feature.

Run checks:
- CHECKS
- git diff --check
- git status --short

Output:
1. Changed files
2. Exact summary
3. Check results
4. Self-review against scope
5. git status --short
6. Suggested commit message
```

## DOCS-only Prompt

```text
Implement docs-only update.

Read only first:
- AGENTS.md
- docs/product/ASSISTANT_WORKFLOW.md
- current_focus.md
- docs/product/PROGRESS.md
- relevant docs only as needed

Scope:
- Docs/process/state only.
- Do not change product code.
- Do not change tests.
- Do not start a new block.

Required changes:
- DOCS_CHANGES

Run:
- git diff --check
- git status --short

Output:
1. Changed files
2. Exact summary
3. git diff --check result
4. git status --short
5. Suggested commit message
```

## BLOCK Closeout Prompt

```text
Implement docs-only BLOCK closeout for BLOCK.

Read only first:
- AGENTS.md
- docs/product/ASSISTANT_WORKFLOW.md
- current_focus.md
- docs/product/PROGRESS.md
- docs/blocks/BLOCK_FILE.md

Scope:
- Docs/state only.
- Do not change product code.
- Do not change tests.
- Do not start the next block.
- Do not overclaim product readiness.

Required changes:
- Mark BLOCK status accurately.
- Record completed features.
- Set next state to awaiting approved planning unless a next step is already approved.

Run:
- git diff --check
- git status --short

Output:
1. Changed files
2. Exact summary
3. git diff --check result
4. git status --short
5. Suggested commit message
```
