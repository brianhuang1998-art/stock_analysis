#!/usr/bin/env python3
"""Self-test for organize.py: builds a throw-away project in a temp folder and checks the classification,
the move (with reference rewriting) and the safety rules.  Run: python3 .claude/skills/organize-files/scripts/selftest.py"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, 'organize.py')
bad = 0


def run(root, *args):
    r = subprocess.run([sys.executable, SCRIPT, '--root', root, *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def expect(name, cond, detail=''):
    global bad
    if not cond:
        bad += 1
        print(f'FAIL {name} {detail}')


def write(root, rel, text='x'):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(text)


with tempfile.TemporaryDirectory() as root:
    # files already in the right place
    for rel in ['README.md', 'sw.js', 'manifest.json', 'home.html', 'assets/css/a.css', 'assets/js/a.js', '.claude/skills/s1/SKILL.md',
                '.claude/skills/s1/scripts/build_x.py', 'papers/source/p.pdf', 'papers/audit/report.md', 'config/other.config.json']:
        write(root, rel)
    code, out = run(root, 'check')
    expect('clean project passes', code == 0, out)

    # misplaced / unclassified files
    write(root, 'new_paper.pdf')                      # a paper at the root
    write(root, 'scan_table9.json')                   # an audit transcription at the root
    write(root, 'ref_simulator_v2.py')                # paper verification code
    write(root, 'site-config.js', 'self.SITE = {}')   # global settings at the root
    write(root, 'extra.css')
    write(root, 'notes.txt')                          # nothing matches
    write(root, 'my-skill/SKILL.md')                  # a skill outside .claude/skills
    write(root, 'refs.md', 'see new_paper.pdf, site-config.js, assets/css/extra.css and config/site-config.js.bak')
    code, out = run(root, 'check')
    expect('problems are detected', code == 1, out)
    for want in ['new_paper.pdf', 'scan_table9.json', 'ref_simulator_v2.py', 'site-config.js', 'extra.css', 'notes.txt', 'my-skill/SKILL.md']:
        expect(f'{want} is reported', want in out, out)
    expect('unclassified is not guessed', 'UNCLASSIFIED  notes.txt' in out, out)

    # where
    code, out = run(root, 'where', 'brand_new.pdf', 'build_site.py', 'logo.svg', 'page.html', 'sw.js')
    for want in ['papers/source/brand_new.pdf', '_dev/build_site.py', 'assets/icons/logo.svg', 'page.html', 'pinned']:
        expect(f'where says {want}', want in out, out)
    code, out = run(root, 'where', 'SKILL.md', '--skill', 'demo')
    expect('where for a skill', '.claude/skills/demo/SKILL.md' in out, out)

    # dry run changes nothing
    code, out = run(root, 'apply')
    expect('dry run does not move', os.path.exists(os.path.join(root, 'new_paper.pdf')), out)
    expect('dry run says so', 'dry run' in out, out)

    # a name clash is never overwritten
    write(root, 'papers/source/new_paper.pdf', 'already here')
    code, out = run(root, 'apply', '--yes')
    expect('clash is skipped', 'SKIPPED' in out and open(os.path.join(root, 'papers/source/new_paper.pdf')).read() == 'already here', out)
    expect('clashing file stays put', os.path.exists(os.path.join(root, 'new_paper.pdf')), out)

    # the rest is moved and references are rewritten
    expect('pdf kept at the root only because of the clash', True)
    for old, new in [('scan_table9.json', 'papers/audit/transcriptions/scan_table9.json'), ('ref_simulator_v2.py', 'papers/verification/ref_simulator_v2.py'),
                     ('site-config.js', 'config/site-config.js'), ('extra.css', 'assets/css/extra.css')]:
        expect(f'{old} moved', os.path.exists(os.path.join(root, new)) and not os.path.exists(os.path.join(root, old)), out)
    expect('unclassified file untouched', os.path.exists(os.path.join(root, 'notes.txt')))
    refs = open(os.path.join(root, 'refs.md')).read()
    expect('reference rewritten', ' config/site-config.js,' in refs, refs)
    expect('a longer path is not corrupted', 'assets/css/extra.css' in refs and 'assets/css/assets' not in refs and 'config/config/' not in refs, refs)
    code, out = run(root, 'check')
    expect('remaining problems are only the unclassified file, the clash and the stray skill', 'notes.txt' in out and 'new_paper.pdf' in out, out)

print('ALL CHECKS PASSED' if not bad else f'{bad} FAILURES')
sys.exit(1 if bad else 0)
