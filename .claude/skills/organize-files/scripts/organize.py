#!/usr/bin/env python3
"""Decide where each file of this project belongs, report files that are in the wrong place, and move them.

  organize.py check [--quiet]               list misplaced and unclassified files (exit code 1 if there are any)
  organize.py where NAME [NAME ...] [--skill SKILL]   say which folder a (new) file should go to
  organize.py apply [--yes] [--no-refs]     move misplaced files (a dry run unless --yes) and rewrite references to them

The rules live in ../rules.json. Standard library only. Nothing is ever overwritten or deleted.
"""
import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(HERE, '..', 'rules.json')
TEXT_EXT = {'.md', '.html', '.js', '.json', '.py', '.sh', '.txt', '.css', '.xml', '.yml', '.yaml', '.toml', ''}


def load_rules(path=RULES_PATH):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def project_root(arg):
    if arg:
        return os.path.abspath(arg)
    try:
        out = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    return os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))


def is_git(root):
    return os.path.isdir(os.path.join(root, '.git'))


def list_files(root, rules):
    """Tracked + untracked (not ignored) files as project-relative paths with forward slashes."""
    files = []
    if is_git(root):
        out = subprocess.run(['git', '-C', root, 'ls-files', '-co', '--exclude-standard'], capture_output=True, text=True).stdout
        files = [p for p in out.split('\n') if p and os.path.exists(os.path.join(root, p))]
    else:
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in rules['ignore']]
            for f in fn:
                files.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/'))
    return sorted(p for p in files if not ignored(p, rules))


def ignored(path, rules):
    parts = path.split('/')
    return any(i in parts or path == i or path.startswith(i + '/') for i in rules['ignore'])


def matches(path, patterns):
    base = path.rsplit('/', 1)[-1]
    for pat in patterns:
        if '/' in pat:
            if fnmatch.fnmatch(path, pat):
                return True
        elif fnmatch.fnmatch(base, pat):
            return True
    return False


def under(path, folder):
    return folder == '' and '/' not in path or (folder != '' and path.startswith(folder.rstrip('/') + '/'))


def classify(path, rules, skill=None):
    """Returns (status, category_id, destination_folder, note).
    status: ok | pinned | misplaced | unclassified | needs-name"""
    if matches(path, rules['pinned']):
        return 'pinned', None, None, 'stays where it is'
    if any(under(path, p) for p in rules.get('protected', [])):
        return 'ok', None, None, ''
    for cat in rules['categories']:
        if not matches(path, cat['match']):
            continue
        dest = cat['dest']
        if '{skill}' in dest:
            name = skill
            if not name:
                parent = path.rsplit('/', 2)[-2] if path.count('/') >= 1 else ''
                name = parent or None
            if not name:
                return 'needs-name', cat['id'], dest, 'give the skill name with --skill'
            dest = dest.replace('{skill}', name)
        if under(path, dest) or (dest != '' and path.startswith(dest + '/')):
            return 'ok', cat['id'], dest, ''
        return 'misplaced', cat['id'], dest, cat.get('label', '')
    if any(under(path, c) for c in rules['containers']):
        return 'ok', None, None, ''
    return 'unclassified', None, None, 'no rule matches this file'


def dest_path(path, dest):
    return (dest + '/' if dest else '') + path.rsplit('/', 1)[-1]


def skill_folders_without_skill_md(root, files):
    bad = []
    seen = set()
    for p in files:
        if p.startswith('.claude/skills/') and p.count('/') >= 3:
            folder = '/'.join(p.split('/')[:3])
            seen.add(folder)
    for folder in sorted(seen):
        if not os.path.exists(os.path.join(root, folder, 'SKILL.md')):
            bad.append(folder)
    return bad


def cmd_check(args, rules, root):
    files = list_files(root, rules)
    misplaced, unclassified, needs = [], [], []
    for p in files:
        status, cid, dest, note = classify(p, rules)
        if status == 'misplaced':
            misplaced.append((p, cid, dest))
        elif status == 'unclassified':
            unclassified.append(p)
        elif status == 'needs-name':
            needs.append(p)
    no_skill_md = skill_folders_without_skill_md(root, files)
    if not args.quiet or misplaced or unclassified or needs or no_skill_md:
        print(f"organize: {len(files)} files checked")
    for p, cid, dest in misplaced:
        print(f"  MISPLACED     {p}\n                -> {dest_path(p, dest)}   ({cid})")
    for p in needs:
        print(f"  NEEDS NAME    {p}\n                -> move it into .claude/skills/<skill-name>/")
    for p in unclassified:
        print(f"  UNCLASSIFIED  {p}\n                -> no rule matches; ask where it belongs, then add a rule to .claude/skills/organize-files/rules.json")
    for f in no_skill_md:
        print(f"  SKILL FOLDER WITHOUT SKILL.md  {f}")
    if not (misplaced or unclassified or needs or no_skill_md):
        if not args.quiet:
            print("  everything is in its place")
        return 0
    print("  fix with: python3 .claude/skills/organize-files/scripts/organize.py apply --yes")
    return 1


def cmd_where(args, rules, root):
    code = 0
    for name in args.names:
        status, cid, dest, note = classify(name, rules, skill=args.skill)
        if status == 'pinned':
            print(f"{name}\n  stays where it is (pinned: needed at its current place)")
        elif status == 'ok' and cid is None:
            print(f"{name}\n  already inside a known folder; no rule applies")
        elif status == 'ok':
            print(f"{name}\n  already in the right place ({cid})")
        elif status == 'needs-name':
            print(f"{name}\n  {note}")
            code = 1
        elif status == 'unclassified':
            print(f"{name}\n  UNCLASSIFIED: {note}. Ask the user, then add a rule to rules.json")
            code = 1
        else:
            print(f"{name}\n  -> {dest_path(name, dest)}   ({cid}: {note})")
    return code


def rewrite_references(root, files, old, new):
    changed = []
    for p in files:
        if os.path.splitext(p)[1].lower() not in TEXT_EXT or p == old:
            continue
        full = os.path.join(root, p)
        try:
            with open(full, encoding='utf-8') as f:
                text = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        # Whole-path matches only: "extra.css" must not be rewritten inside "assets/css/extra.css"
        pattern = re.compile(r'(?<![\w./-])' + re.escape(old) + r'(?![\w-]|\.\w)')
        updated, n = pattern.subn(new, text)
        if n:
            with open(full, 'w', encoding='utf-8') as f:
                f.write(updated)
            changed.append(p)
    return changed


def cmd_apply(args, rules, root):
    files = list_files(root, rules)
    plan = []
    for p in files:
        status, cid, dest, note = classify(p, rules)
        if status == 'misplaced':
            target = dest_path(p, dest)
            plan.append((p, target, cid))
    if not plan:
        print("organize: nothing to move")
        return 0
    taken = set(files)
    for old, new, cid in plan:
        print(f"  {old}\n    -> {new}   ({cid})")
        if new in taken:
            print("    SKIPPED: a file with that name is already there (nothing is overwritten)")
    if not args.yes:
        print("dry run only. Run again with --yes to move the files" + ("" if args.no_refs else " and rewrite references to them") + ".")
        return 0
    moved = []
    for old, new, cid in plan:
        if new in taken:
            continue
        os.makedirs(os.path.dirname(os.path.join(root, new)) or root, exist_ok=True)
        tracked = is_git(root) and subprocess.run(['git', '-C', root, 'ls-files', '--error-unmatch', old],
                                                  capture_output=True).returncode == 0
        if tracked:
            subprocess.run(['git', '-C', root, 'mv', old, new], check=True)
        else:
            shutil.move(os.path.join(root, old), os.path.join(root, new))
        moved.append((old, new))
        taken.add(new)
    print(f"moved {len(moved)} file(s)")
    if not args.no_refs:
        files = list_files(root, rules)
        for old, new in moved:
            changed = rewrite_references(root, files, old, new)
            print(f"  references to {old}: rewrote {len(changed)} file(s)" + (": " + ", ".join(changed[:6]) + (" ..." if len(changed) > 6 else "") if changed else ""))
        print("  note: only exact path strings are rewritten. Search for the file's name for references built from pieces,")
        print("  then run python3 _dev/build.py if a page or the global settings moved.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', help='project root (default: the git root)')
    ap.add_argument('--rules', default=RULES_PATH)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check'); c.add_argument('--quiet', action='store_true')
    w = sub.add_parser('where'); w.add_argument('names', nargs='+'); w.add_argument('--skill')
    a = sub.add_parser('apply'); a.add_argument('--yes', action='store_true'); a.add_argument('--no-refs', action='store_true')
    args = ap.parse_args()
    rules = load_rules(args.rules)
    root = project_root(args.root)
    sys.exit({'check': cmd_check, 'where': cmd_where, 'apply': cmd_apply}[args.cmd](args, rules, root))


if __name__ == '__main__':
    main()
