---
name: organize-files
description: Put every new file of this project in the right folder (Claude Code skills, paper files, global settings, website pages, assets, development tools), report files that are misplaced, and move them without breaking references. Use whenever you are about to create, save, generate, download or move a file in this project, when the user says they added a file, or when asked to tidy up or check the folder structure. It runs a script that applies the rules in rules.json, so the placement is decided by rules, not by guessing.
---

# Organize files

Where a file goes is decided by `rules.json` and applied by `scripts/organize.py`. Do not decide by feel and do not move files by hand: moving a file also has to fix everything that points to it.

## The folders (summary)
| What the file is | Goes to |
|---|---|
| A Claude Code skill (`SKILL.md` and its scripts and references) | `.claude/skills/<skill-name>/` (Claude Code only finds skills there) |
| The paper PDF | `papers/source/` |
| Table transcriptions of the paper | `papers/audit/transcriptions/` |
| Paper audit reports, check outputs, inventories | `papers/audit/` |
| Paper vs our code: comparison notes, simulators, analyses | `papers/verification/` |
| Global (site-wide) settings, e.g. `site-config.js` | `config/` |
| Website pages (`*.html`) | project root (a page's URL is its file name, so it must not move) |
| Website styles / scripts / icons | `assets/css/`, `assets/js/`, `assets/icons/` |
| Website development tools (`build*.py`, templates) | `_dev/` |
| Stay where they are (needed at their place) | `README.md`, `.gitignore`, `manifest.json`, `sw.js`, `sitemap.xml`, `.githooks/*`, `.claude/settings*.json` |

Full list with the reasons: `references/categories.md`.

## When you create a file
1. **Before saving it**, ask where it belongs:
   ```bash
   python3 .claude/skills/organize-files/scripts/organize.py where <file name> [--skill <skill-name>]
   ```
   Save it in the folder it prints. For a new skill, create `.claude/skills/<skill-name>/SKILL.md` (use `--skill` to say the name).
2. **After a batch of changes** run `python3 .claude/skills/organize-files/scripts/organize.py check`. It lists misplaced files, unclassified files and skill folders without `SKILL.md`.
3. If something is misplaced, look at the plan first, then move:
   ```bash
   python3 .claude/skills/organize-files/scripts/organize.py apply        # dry run: shows what would move
   python3 .claude/skills/organize-files/scripts/organize.py apply --yes  # moves (git mv when tracked) and rewrites exact path references
   ```
4. After moving, search for the file name for references the script cannot rewrite (paths built from pieces such as `ROOT / 'assets' / 'js'`), fix them, and run `python3 _dev/build.py` if a page or the global settings moved. Then run the project's checks.

## When the script says UNCLASSIFIED
No rule matches the file. **Ask the user** which category it belongs to, do not guess. Then add a rule to `rules.json` (a category with `match` patterns and a `dest`) so the next file of that kind is placed automatically, and update the folder structure in `README.md`.

## When you add a new kind of folder
Add the folder to `containers` and a category to `rules.json`, then update `README.md` (the folder tree and the table of files) and `papers/README.md` if it is under `papers/`.

## Rules the script follows
- Pinned files never move. Files inside `.claude/skills/` are never moved out of their skill, whatever their name is.
- Nothing is overwritten or deleted: if the destination already has a file with that name the move is skipped and reported.
- `apply` is a dry run unless `--yes` is given.
- Moves use `git mv` for tracked files, so history is kept.
- Only whole path strings are rewritten in text files; a longer path that merely contains the old name is left alone.

## Limits
- A skill cannot watch the file system. It runs when Claude is about to create or move a file, when asked, and the pre-commit hook prints a warning (it never blocks a commit). A file the user drops in by hand is caught by `check` or at the next commit.
- Classification is by file name and extension. The same name in the wrong context (a `.json` that is not a paper transcription) is reported as unclassified, not guessed.

## Check the tool itself
`python3 .claude/skills/organize-files/scripts/selftest.py` builds a throw-away project and checks classification, dry run, clash handling and reference rewriting.
