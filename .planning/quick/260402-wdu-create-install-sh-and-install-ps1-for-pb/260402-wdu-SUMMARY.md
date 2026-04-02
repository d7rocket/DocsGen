---
phase: quick
plan: 260402-wdu
subsystem: installer
tags: [install, bash, powershell, skill-distribution]
dependency_graph:
  requires: [.claude/skills/pbi-docgen/*]
  provides: [install.sh, install.ps1, .claude/commands/pbi-docgen.md]
  affects: [skill installation UX]
tech_stack:
  added: []
  patterns: [curl-pipe-bash installer, irm-pipe-iex installer]
key_files:
  created:
    - install.sh
    - install.ps1
    - .claude/commands/pbi-docgen.md
  modified: []
decisions:
  - "Helper function pattern for DRY download calls in both scripts"
  - "UseBasicParsing flag in PowerShell for compatibility without IE engine"
metrics:
  duration: 1m
  completed: 2026-04-02
---

# Quick Task 260402-wdu: Create install.sh and install.ps1 Summary

Bash and PowerShell one-liner installers that download all 23 pbi-docgen skill files from GitHub raw, register the /pbi-docgen command, install Python dependencies, and set up Playwright Chromium.

## Tasks Completed

| # | Task | Commit | Key Files |
|---|------|--------|-----------|
| 1 | Command registration + install.sh | f4895a9 | install.sh, .claude/commands/pbi-docgen.md |
| 2 | install.ps1 PowerShell installer | 1641e36 | install.ps1 |

## What Was Built

**install.sh** -- Bash installer using `curl -sL` with a `download()` helper function. Creates directory structure under `~/.claude/skills/pbi-docgen/`, downloads all 23 skill files and the command registration file, runs `pip install` for Python dependencies, installs Playwright Chromium, and prints a green success banner.

**install.ps1** -- PowerShell installer mirroring install.sh logic with native idioms (`Invoke-WebRequest`, `New-Item`, `Write-Host`). Uses `$ErrorActionPreference = 'Stop'` for fail-fast behavior and `-UseBasicParsing` for broad compatibility.

**.claude/commands/pbi-docgen.md** -- Command registration file that enables `/pbi-docgen` in Claude Code, pointing to the skill at `~/.claude/skills/pbi-docgen/SKILL.md`.

**One-liner install commands:**
- Bash: `curl -sL https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.sh | bash`
- PowerShell: `irm https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.ps1 | iex`

## Deviations from Plan

None -- plan executed exactly as written.

## Known Stubs

None.

## Verification Results

- install.sh passes `bash -n` syntax check
- install.ps1 is readable by PowerShell
- .claude/commands/pbi-docgen.md exists with SKILL.md reference
- Both scripts download exactly 23 skill files
- Both scripts include pip install and playwright install chromium steps

## Self-Check: PASSED

All 3 created files verified on disk. Both commit hashes (f4895a9, 1641e36) confirmed in git log.
