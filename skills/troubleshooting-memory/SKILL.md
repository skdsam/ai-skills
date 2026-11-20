---
name: troubleshooting-memory
description: Use automatically whenever an error, bug, test failure, or unexpected behavior is encountered. This skill mandates checking the global categorized troubleshooting logs for known fixes.
---

# Troubleshooting Memory Skill

## Overview
This skill ensures that we never waste time solving the same problem twice. It mandates a "Look-back" phase at the very start of any debugging process.

## Triggers
- Any keyword: `error`, `failed`, `bug`, `issue`, `not working`, `fix`, `troubleshoot`.
- Any terminal command that returns a non-zero exit code.
- Any test suite failure.

## Mandatory Instructions

### 1. Identify Category
Determine the technology category of the current issue (e.g., `tauri`, `blender`, `rust`, `javascript`, `react`, etc.).

### 2. Check the Global Logs
**BEFORE attempting ANY research or fix**, you MUST check the corresponding log file in the global troubleshooting directory:
`C:\Users\skdso\.gemini\antigravity\troubleshooting_logs/`

- Use `list_dir` on that folder to see the available categories.
- Use `grep_search` on the relevant `.md` file for keywords matching the current error.
- Use `view_file` to read the entry if a match is found.

### 3. Evaluate the Logged Fix
- If a fix exists, try it immediately.
- If the fix fails OR no fix exists, proceed to standard debugging (e.g., `@systematic-debugging`).

### 4. Update the Log
Once a NEW issue is resolved, you **MUST** update the relevant log file (or create a new category file) with the following format:

```markdown
### [YYYY-MM-DD] Short Title of Issue
- **Issue**: Description of the symptom.
- **Failed Attempts**: What we tried that didn't work.
- **Root Cause**: Why it was actually happening.
- **Fix**: The exact code change or command that resolved it.
```

## The Command
If the user points to this skill or asks to "Check the logs", use this protocol.
