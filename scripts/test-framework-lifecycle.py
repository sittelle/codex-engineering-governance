#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION=(ROOT/'VERSION').read_text().strip()
MANAGED_RE=re.compile(r'(?s)<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->.*?<!-- END CODEX-GOVERNANCE-MANAGED -->')
TEMPLATE_AGENTS=(ROOT/'templates/repository/AGENTS.md').read_text(encoding='utf-8')
TEMPLATE_MANAGED_MATCH=MANAGED_RE.search(TEMPLATE_AGENTS)
TEMPLATE_MANAGED=TEMPLATE_MANAGED_MATCH.group(0) if TEMPLATE_MANAGED_MATCH else ''
PROPAGATION_MARKERS=(
    'Known vulnerability/finding risk acceptance is distinct from missing required-control evidence',
    'separate explicit governance/policy exception',
    'Reassess a `NOT_APPLICABLE` decision when its factual trigger changes',
    'Changing result classification for a required security control is a material C2 assurance-policy change',
    'same clean commit, verification plan, managed assurance baseline, runner semantics, and required-check inventory',
    'An attributable executed `FAIL` remains fail-dominant',
    'Service restoration is not governance completion',
    'after stabilization, run deferred verification',
    'Required-control response completeness',
    'finding risk acceptance is not the governance/policy exception required to proceed without the control',
    'any attributable executed `FAIL` remains fail-dominant even when another approved context passes',
    'A complete emergency answer explicitly states both post-stabilization duties',
    'Mentioning only deferred verification is incomplete',
)
GLOBAL_KERNEL_MARKERS=(
    '## Required-control response completeness',
    'finding-risk acceptance cannot substitute for that missing-control exception',
    'any attributable executed `FAIL` remains fail-dominant even if another approved context reports PASS',
    '### Emergency-response completeness',
    'Mentioning only deferred verification is incomplete',
)
WORKFLOW_COMPLETENESS_MARKERS={
    'workflows/release/WORKFLOW.md': (
        '## Required-control response completeness',
        'known vulnerability/finding is a different decision from granting a governance/policy exception',
        'an attributable executed `FAIL` remains fail-dominant',
    ),
    'workflows/emergency-fix/WORKFLOW.md': (
        '### Emergency-response completeness',
        'complete/reconcile deferred verification',
        'review and remove or deliberately reconcile temporary bypasses',
    ),
}
OLD_MANAGED='''<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->
## Central governance integration

This is deliberately an older managed block used by lifecycle regression.
<!-- END CODEX-GOVERNANCE-MANAGED -->'''

def run(argv,cwd=None,env=None): return subprocess.run(argv,cwd=cwd,text=True,capture_output=True,check=False,env=env)
def copy_template_project(target):
    target.mkdir(parents=True,exist_ok=True)
    for rel in ('AGENTS.md','project-governance.yml','verification-plan.json','.gitignore'):
        shutil.copy2(ROOT/'templates/repository'/rel,target/rel)
def assert_true(cond,msg,failures):
    if not cond: failures.append(msg)

def _bounded_output(result, limit=1200):
    text = "\n".join(x.strip() for x in (result.stdout or "", result.stderr or "") if x and x.strip())
    if len(text) > limit:
        text = text[-limit:]
    return text

def _powershell_trust_block(text):
    lower=text.lower()
    needles=(
        'running scripts is disabled', 'cannot be loaded because running scripts is disabled',
        'is not digitally signed', 'pssecurityexception',
        'execution policies', 'authorizationmanager check failed',
    )
    return any(n in lower for n in needles)

def command_ok(result,label,failures,powershell=False):
    if result.returncode == 0:
        return True
    detail=_bounded_output(result)
    msg=f'{label} (exit {result.returncode})'
    if powershell and _powershell_trust_block(detail):
        msg += '; PowerShell trust policy blocked script execution. Verify the release/archive identity and deliberately Unblock-File the trusted archive/scripts; do not bypass execution policy.'
    if detail:
        msg += ': ' + detail
    failures.append(msg)
    return False

def require_dir(path,label,failures):
    if path.is_dir():
        return True
    failures.append(f'{label}: expected directory is missing: {path}')
    return False

def technology_baseline(text):
    state=re.search(r'(?m)^technology_baseline:\s*\n[ \t]+state:\s*"([^"]+)"',text)
    record=re.search(r'(?m)^technology_baseline:\s*\n(?:[ \t]+[^\n]*\n)*?[ \t]+record:\s*"([^"]+)"',text)
    return (state.group(1) if state else None, record.group(1) if record else None)

def managed_block(text):
    match=MANAGED_RE.search(text)
    return match.group(0) if match else None

def assert_managed_template(text,label,failures):
    actual=managed_block(text)
    assert_true(bool(TEMPLATE_MANAGED),f'{label}: template managed block missing',failures)
    assert_true(actual==TEMPLATE_MANAGED,f'{label}: installed managed block differs from authoritative template block',failures)
    if actual:
        for marker in PROPAGATION_MARKERS:
            assert_true(marker in actual,f'{label}: propagation-critical managed guidance missing {marker}',failures)
        for marker in ('feature implementation proposes','workflows/new-feature/WORKFLOW.md','Technology Baseline Transition Summary','Delta/classification','Technical recommendation','Dependency/supply-chain','Approval state','Transition state/durable record','RECONCILIATION_REQUIRED','Verification/assurance reconciliation','newly applicable capabilities','`ESTABLISHED` closure criteria','NOT APPLICABLE'):
            assert_true(marker in actual,f'{label}: managed Technology Baseline transition guidance missing {marker}',failures)

def with_old_managed(text):
    return MANAGED_RE.sub(OLD_MANAGED,text,count=1)



def init_activation_fixture(base, old_version, *, fail_full=False):
    fixture=base/'eval-fixture'; fixture.mkdir(parents=True)
    shutil.copy2(ROOT/'templates/repository/AGENTS.md',fixture/'AGENTS.md')
    manifest=(ROOT/'templates/repository/project-governance.yml').read_text(encoding='utf-8')
    manifest=manifest.replace(f'baseline: "{VERSION}"',f'baseline: "{old_version}"',1)
    (fixture/'project-governance.yml').write_text(manifest,encoding='utf-8',newline='\n')
    tests=fixture/'tests'; tests.mkdir()
    full_return='1' if fail_full else '0'
    verifier=(
        '#!/usr/bin/env python3\n'
        'from pathlib import Path\n'
        'import sys\n'
        f"EXPECTED = 'baseline: \"{old_version}\"'\n"
        '\n'
        'def main():\n'
        '    root=Path(__file__).resolve().parents[1]\n'
        "    text=(root/'project-governance.yml').read_text(encoding='utf-8-sig')\n"
        "    mode=sys.argv[1] if len(sys.argv)>1 else 'quick'\n"
        '    if EXPECTED not in text:\n'
        "        print('Evaluation fixture verification: FAIL')\n"
        '        return 1\n'
        "    if mode == 'full':\n"
        f'        return {full_return}\n'
        "    print(f'Evaluation fixture verification: PASS ({mode})')\n"
        '    return 0\n'
        '\n'
        "if __name__ == '__main__':\n"
        '    raise SystemExit(main())\n'
    )
    (tests/'eval-verification.py').write_text(verifier,encoding='utf-8',newline='\n')
    run(['git','init','-q'],cwd=fixture)
    run(['git','config','user.email','activation@example.invalid'],cwd=fixture)
    run(['git','config','user.name','Activation Test'],cwd=fixture)
    run(['git','add','-A'],cwd=fixture)
    committed=run(['git','commit','-qm','fixture baseline'],cwd=fixture)
    if committed.returncode != 0:
        raise RuntimeError(committed.stdout+committed.stderr)
    return fixture

def activation_snapshot(root):
    return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}

def test_common(failures):
    assert_true(bool(TEMPLATE_MANAGED),'authoritative template managed block missing',failures)
    kernel=(ROOT/'codex-home/AGENTS.md').read_text(encoding='utf-8')
    for marker in GLOBAL_KERNEL_MARKERS:
        assert_true(marker in kernel,f'global kernel response-completeness guidance missing {marker}',failures)
    for rel, markers in WORKFLOW_COMPLETENESS_MARKERS.items():
        workflow=(ROOT/rel).read_text(encoding='utf-8')
        for marker in markers:
            assert_true(marker in workflow,f'{rel}: response-completeness guidance missing {marker}',failures)
    for rel in ('scripts/manage-governed-project.ps1','scripts/manage-governed-project.sh','scripts/update-governed-project.ps1','scripts/update-governed-project.sh'):
        lifecycle=(ROOT/rel).read_text(encoding='utf-8')
        assert_true('## Central governance integration' not in lifecycle,f'{rel}: hard-codes managed AGENTS content instead of sourcing template',failures)
    assert_managed_template(TEMPLATE_AGENTS,'template',failures)
    candidate_tools=run([sys.executable,str(ROOT/'scripts/test-candidate-validation.py')])
    if not command_ok(candidate_tools,'candidate validation tooling regression failed',failures): return
    activation=ROOT/'scripts/activate-frozen-baseline.py'
    old_version='0.5.24' if VERSION!='0.5.24' else '0.5.23'
    with tempfile.TemporaryDirectory(prefix='gov-activation-test-') as td:
        base=Path(td); fixture=init_activation_fixture(base,old_version); codex_home=base/'codex-home'; codex_home.mkdir()
        (codex_home/'AGENTS.md').write_text('previous kernel\n',encoding='utf-8',newline='\n')
        (codex_home/'GOVERNANCE_ROOT').write_text('previous-root',encoding='utf-8',newline='\n')
        before_fixture=activation_snapshot(fixture); before_home=activation_snapshot(codex_home)
        before_agents=(fixture/'AGENTS.md').read_bytes()
        dry=run([sys.executable,str(activation),'--fixture',str(fixture),'--codex-home',str(codex_home)])
        if not command_ok(dry,'frozen baseline activation dry-run failed',failures): return
        assert_true('Frozen baseline activation dry-run: PASS' in dry.stdout,'activation dry-run missing PASS summary',failures)
        assert_true(activation_snapshot(fixture)==before_fixture and activation_snapshot(codex_home)==before_home,'activation dry-run mutated fixture or Codex home',failures)
        applied=run([sys.executable,str(activation),'--fixture',str(fixture),'--codex-home',str(codex_home),'--apply'])
        if not command_ok(applied,'frozen baseline activation apply failed',failures): return
        assert_true('Frozen baseline activation: PASS' in applied.stdout,'activation apply missing PASS summary',failures)
        manifest=(fixture/'project-governance.yml').read_text(encoding='utf-8-sig')
        verifier=(fixture/'tests/eval-verification.py').read_text(encoding='utf-8-sig')
        assert_true(f'baseline: "{VERSION}"' in manifest and f'baseline: "{VERSION}"' in verifier,'activation did not reconcile fixture baseline/assertion',failures)
        status=run(['git','status','--porcelain=v1','--untracked-files=all'],cwd=fixture).stdout.splitlines()
        status_paths={line[3:].replace('\\','/') for line in status if line}
        assert_true(status_paths=={'project-governance.yml','tests/eval-verification.py'},'activation did not recognize byte-equivalent AGENTS or produced unexpected fixture changes: '+repr(status),failures)
        assert_true((fixture/'AGENTS.md').read_bytes()==before_agents,'activation changed exact AGENTS bytes despite an already-authoritative managed block',failures)
        assert_true(not any(fixture.glob('*.governance-backup-*')),'activation left updater backup artifacts in fixture',failures)
        assert_true((codex_home/'AGENTS.md').read_bytes()==(ROOT/'codex-home/AGENTS.md').read_bytes(),'activation global kernel installation mismatch',failures)
        assert_true((codex_home/'GOVERNANCE_ROOT').read_text(encoding='utf-8-sig').strip()==str(ROOT.resolve()),'activation GOVERNANCE_ROOT mismatch',failures)
        assert_true(any(codex_home.glob('AGENTS.md.backup-*')),'activation did not retain global kernel backup',failures)

    with tempfile.TemporaryDirectory(prefix='gov-activation-rollback-test-') as td:
        base=Path(td); fixture=init_activation_fixture(base,old_version,fail_full=True); codex_home=base/'codex-home'; codex_home.mkdir()
        (codex_home/'AGENTS.md').write_text('previous kernel\n',encoding='utf-8',newline='\n')
        (codex_home/'GOVERNANCE_ROOT').write_text('previous-root',encoding='utf-8',newline='\n')
        before_fixture=activation_snapshot(fixture); before_home=activation_snapshot(codex_home)
        failed=run([sys.executable,str(activation),'--fixture',str(fixture),'--codex-home',str(codex_home),'--apply'])
        assert_true(failed.returncode!=0 and 'Activation rollback: PASS' in failed.stderr,'activation did not fail/rollback after fixture verification failure',failures)
        assert_true(activation_snapshot(fixture)==before_fixture and not run(['git','status','--porcelain=v1','--untracked-files=all'],cwd=fixture).stdout.strip(),'activation rollback did not restore clean fixture bytes',failures)
        assert_true(activation_snapshot(codex_home)==before_home,'activation rollback unexpectedly changed global Codex home before install',failures)

    with tempfile.TemporaryDirectory(prefix='gov-activation-dirty-test-') as td:
        base=Path(td); fixture=init_activation_fixture(base,old_version); codex_home=base/'codex-home'
        (fixture/'project-governance.yml').write_text((fixture/'project-governance.yml').read_text(encoding='utf-8')+'# dirty\n',encoding='utf-8',newline='\n')
        before=activation_snapshot(fixture)
        dirty=run([sys.executable,str(activation),'--fixture',str(fixture),'--codex-home',str(codex_home),'--apply'])
        assert_true(dirty.returncode!=0 and 'worktree is dirty' in dirty.stderr,'activation accepted dirty fixture worktree',failures)
        assert_true(activation_snapshot(fixture)==before,'activation mutated dirty fixture before refusal',failures)
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'project'; copy_template_project(project)
        bootstrap=ROOT/'scripts/bootstrap-assurance.py'
        before={p.relative_to(project).as_posix():p.read_bytes() for p in project.rglob('*') if p.is_file()}
        d=run([sys.executable,str(bootstrap),'--project-root',str(project),'--allow-unconfigured-ci'])
        if not command_ok(d,'assurance bootstrap dry-run failed',failures): return
        after={p.relative_to(project).as_posix():p.read_bytes() for p in project.rglob('*') if p.is_file()}
        assert_true(before==after and not (project/'.governance').exists(),'assurance bootstrap dry-run mutated project',failures)
        a=run([sys.executable,str(bootstrap),'--project-root',str(project),'--allow-unconfigured-ci','--apply'])
        if not command_ok(a,'assurance bootstrap apply failed',failures): return
        for rel in ('.governance/run-verification.py','.governance/run-ci-verification.py','.governance/aggregate-verification.py','.governance/assurance-baseline.json','.governance/assurance-bootstrap.json'):
            assert_true((project/rel).exists(),f'assurance bootstrap missing {rel}',failures)
        owned=project/'.governance/run-verification.py'; owned.write_text('# project owned\n')
        again=run([sys.executable,str(bootstrap),'--project-root',str(project),'--allow-unconfigured-ci','--apply'])
        assert_true(again.returncode==0 and owned.read_text()=='# project owned\n','assurance bootstrap overwrote project-owned runner',failures)

def test_posix(failures):
    sh=shutil.which('sh')
    if not sh: failures.append('POSIX sh unavailable'); return
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); home=base/'codex'; env=os.environ.copy(); env['CODEX_HOME']=str(home)
        i=run([sh,str(ROOT/'codex-home/install.sh'),str(ROOT)],env=env)
        if not command_ok(i,'POSIX installer failed',failures): return
        assert_true((home/'AGENTS.md').exists() and (home/'GOVERNANCE_ROOT').read_text()==str(ROOT),'POSIX installer locator/kernel incorrect',failures)
        parent=base/'projects'; parent.mkdir(); target=parent/'Demo'
        preview=run([sh,str(ROOT/'scripts/manage-governed-project.sh'),'New','--parent',str(parent),'--name','Demo','--no-git-init'])
        assert_true(preview.returncode==0 and not target.exists(),'POSIX New preview mutated target',failures)
        apply=run([sh,str(ROOT/'scripts/manage-governed-project.sh'),'New','--parent',str(parent),'--name','Demo','--no-git-init','--apply'])
        if not command_ok(apply,'POSIX New apply failed',failures): return
        assert_true((target/'AGENTS.md').exists(),'POSIX New apply missing AGENTS.md',failures)
        assert_managed_template((target/'AGENTS.md').read_text(),'POSIX New',failures)
        if not (require_dir(target/'src','POSIX New',failures) and require_dir(target/'tests','POSIX New',failures)): return
        assert_true(not any((target/'src').iterdir()) and not any((target/'tests').iterdir()),'POSIX New generated application content',failures)
        manifest=target/'project-governance.yml'
        new_state,new_record=technology_baseline(manifest.read_text())
        assert_true(new_state=='UNESTABLISHED' and new_record=='docs/design.md#technology-baseline','POSIX New technology baseline state/pointer incorrect',failures)
        # Update must preserve project-owned instructions and non-managed manifest decisions, including Technology Baseline.
        agents=target/'AGENTS.md'; agents.write_text(with_old_managed(agents.read_text()).rstrip()+'\n\nLOCAL_KEEP\n')
        text=manifest.read_text().replace(f'baseline: "{VERSION}"','baseline: "0.4.0"',1)
        text=text.replace('state: "UNESTABLISHED"','state: "ESTABLISHED"',1).replace('record: "docs/design.md#technology-baseline"','record: "docs/design.md#approved-technology-baseline"',1)
        manifest.write_text(text)
        up=run([sh,str(ROOT/'scripts/update-governed-project.sh'),str(target),'--apply'])
        if not command_ok(up,'POSIX governed update failed',failures): return
        updated=manifest.read_text()
        updated_state,updated_record=technology_baseline(updated)
        assert_true(f'baseline: "{VERSION}"' in updated and 'LOCAL_KEEP' in agents.read_text(),'POSIX update failed preservation/baseline boundary',failures)
        assert_true(updated_state=='ESTABLISHED' and updated_record=='docs/design.md#approved-technology-baseline','POSIX update changed project-owned Technology Baseline',failures)
        assert_managed_template(agents.read_text(),'POSIX update',failures)
        assert_true('deliberately an older managed block' not in agents.read_text(),'POSIX update failed to propagate newly managed guidance',failures)
        first_agents=agents.read_text(); first_manifest=manifest.read_text()
        up2=run([sh,str(ROOT/'scripts/update-governed-project.sh'),str(target),'--apply'])
        if not command_ok(up2,'POSIX second governed update failed',failures): return
        assert_true(agents.read_text()==first_agents and manifest.read_text()==first_manifest,'POSIX update is not content-idempotent',failures)
        assert_true(any(target.glob('AGENTS.md.governance-backup-*')) and any(target.glob('project-governance.yml.governance-backup-*')),'POSIX update did not create backups',failures)
        # Updating a legacy governed project that predates Technology Baseline must add a truthful reconciliation state.
        legacy=parent/'Legacy'; copy_template_project(legacy)
        legacy_manifest=legacy/'project-governance.yml'
        legacy_text=legacy_manifest.read_text().replace(f'baseline: "{VERSION}"','baseline: "0.4.0"',1)
        legacy_text=re.sub(r'(?ms)^# Governed architecture-significant technology state\.\n# Allowed states:.*?^platforms:', 'platforms:', legacy_text, count=1)
        legacy_text=legacy_text.replace('  languages: []','  languages: ["PROJECT_KEEP"]',1)
        legacy_manifest.write_text(legacy_text)
        legacy_up=run([sh,str(ROOT/'scripts/update-governed-project.sh'),str(legacy),'--apply'])
        if not command_ok(legacy_up,'POSIX legacy governed update failed',failures): return
        legacy_updated=legacy_manifest.read_text()
        legacy_state,legacy_record=technology_baseline(legacy_updated)
        assert_true(f'baseline: "{VERSION}"' in legacy_updated,'POSIX legacy update did not repin governance baseline',failures)
        assert_true(legacy_state=='RECONCILIATION_REQUIRED' and legacy_record=='docs/design.md#technology-baseline','POSIX legacy update did not add Technology Baseline reconciliation state/pointer',failures)
        assert_true('languages: ["PROJECT_KEEP"]' in legacy_updated,'POSIX legacy update overwrote project-owned manifest content',failures)
        # Adopt clean repository must mark both adoption and Technology Baseline reconciliation.
        adopt_clean=base/'existing-clean'; adopt_clean.mkdir(); (adopt_clean/'keep.txt').write_text('v1'); (adopt_clean/'AGENTS.md').write_text('# Project instructions\n\nADOPT_KEEP\n')
        run(['git','init'],cwd=adopt_clean); run(['git','config','user.email','gov@example.invalid'],cwd=adopt_clean); run(['git','config','user.name','Gov'],cwd=adopt_clean); run(['git','add','.'],cwd=adopt_clean); run(['git','commit','-m','base'],cwd=adopt_clean)
        adopted=run([sh,str(ROOT/'scripts/manage-governed-project.sh'),'Adopt','--project',str(adopt_clean),'--no-git-init','--apply'])
        if not command_ok(adopted,'POSIX Adopt clean repository failed',failures): return
        adopted_text=(adopt_clean/'project-governance.yml').read_text()
        adopted_state,_=technology_baseline(adopted_text)
        assert_true(adopted_state=='RECONCILIATION_REQUIRED' and 'adoption:\n  state: "RECONCILIATION_REQUIRED"' in adopted_text,'POSIX Adopt did not require Technology Baseline reconciliation',failures)
        adopted_agents=(adopt_clean/'AGENTS.md').read_text()
        assert_true('ADOPT_KEEP' in adopted_agents,'POSIX Adopt overwrote project-owned AGENTS text',failures)
        assert_managed_template(adopted_agents,'POSIX Adopt',failures)
        # Adopt dirty Git repository must refuse without mutation.
        adopt=base/'existing'; adopt.mkdir(); (adopt/'keep.txt').write_text('v1')
        run(['git','init'],cwd=adopt); run(['git','config','user.email','gov@example.invalid'],cwd=adopt); run(['git','config','user.name','Gov'],cwd=adopt); run(['git','add','.'],cwd=adopt); run(['git','commit','-m','base'],cwd=adopt); (adopt/'keep.txt').write_text('dirty')
        bad=run([sh,str(ROOT/'scripts/manage-governed-project.sh'),'Adopt','--project',str(adopt),'--no-git-init','--apply'])
        assert_true(bad.returncode!=0 and not (adopt/'project-governance.yml').exists(),'POSIX Adopt accepted dirty Git worktree',failures)
        # Bootstrap shell wrapper must route to the same Python bootstrap.
        bs=run([sh,str(ROOT/'scripts/bootstrap-assurance.sh'),'--project-root',str(target),'--allow-unconfigured-ci'])
        command_ok(bs,'POSIX assurance bootstrap wrapper failed',failures)

def powershell(): return shutil.which('pwsh') or shutil.which('powershell') or shutil.which('powershell.exe')
def test_windows(failures):
    ps=powershell()
    if not ps: failures.append('PowerShell unavailable'); return
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); home=base/'codex'
        i=run([ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'codex-home/install.ps1'),'-GovernanceRoot',str(ROOT),'-CodexHome',str(home)])
        if not command_ok(i,'Windows installer failed',failures,powershell=True): return
        locator=(home/'GOVERNANCE_ROOT')
        assert_true((home/'AGENTS.md').exists() and locator.exists() and locator.read_text(encoding='utf-8-sig')==str(ROOT),'Windows installer locator/kernel incorrect',failures)
        parent=base/'projects'; parent.mkdir(); target=parent/'Demo'
        base_cmd=[ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'scripts/manage-governed-project.ps1'),'-Mode','New','-ParentRoot',str(parent),'-ProjectName','Demo','-NoGitInit']
        preview=run(base_cmd); assert_true(preview.returncode==0 and not target.exists(),'Windows New preview mutated target',failures)
        apply=run(base_cmd+['-Apply'])
        if not command_ok(apply,'Windows New apply failed',failures,powershell=True): return
        assert_true((target/'AGENTS.md').exists(),'Windows New apply missing AGENTS.md',failures)
        assert_managed_template((target/'AGENTS.md').read_text(encoding='utf-8-sig'),'Windows New',failures)
        if not (require_dir(target/'src','Windows New',failures) and require_dir(target/'tests','Windows New',failures)): return
        assert_true(not any((target/'src').iterdir()) and not any((target/'tests').iterdir()),'Windows New generated application content',failures)
        manifest=target/'project-governance.yml'
        new_state,new_record=technology_baseline(manifest.read_text(encoding='utf-8-sig'))
        assert_true(new_state=='UNESTABLISHED' and new_record=='docs/design.md#technology-baseline','Windows New technology baseline state/pointer incorrect',failures)
        agents=target/'AGENTS.md'; agents.write_text(with_old_managed(agents.read_text(encoding='utf-8-sig')).rstrip()+'\n\nLOCAL_KEEP\n',encoding='utf-8')
        text=manifest.read_text(encoding='utf-8-sig').replace(f'baseline: "{VERSION}"','baseline: "0.4.0"',1)
        text=text.replace('state: "UNESTABLISHED"','state: "ESTABLISHED"',1).replace('record: "docs/design.md#technology-baseline"','record: "docs/design.md#approved-technology-baseline"',1)
        manifest.write_text(text,encoding='utf-8')
        up=run([ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'scripts/update-governed-project.ps1'),'-ProjectRoot',str(target),'-Apply'])
        if not command_ok(up,'Windows governed update failed',failures,powershell=True): return
        updated=manifest.read_text(encoding='utf-8-sig')
        updated_state,updated_record=technology_baseline(updated)
        assert_true(f'baseline: "{VERSION}"' in updated and 'LOCAL_KEEP' in agents.read_text(encoding='utf-8-sig'),'Windows update failed preservation/baseline boundary',failures)
        assert_true(updated_state=='ESTABLISHED' and updated_record=='docs/design.md#approved-technology-baseline','Windows update changed project-owned Technology Baseline',failures)
        assert_managed_template(agents.read_text(encoding='utf-8-sig'),'Windows update',failures)
        assert_true('deliberately an older managed block' not in agents.read_text(encoding='utf-8-sig'),'Windows update failed to propagate newly managed guidance',failures)
        first_agents=agents.read_text(encoding='utf-8-sig'); first_manifest=manifest.read_text(encoding='utf-8-sig')
        up2=run([ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'scripts/update-governed-project.ps1'),'-ProjectRoot',str(target),'-Apply'])
        if not command_ok(up2,'Windows second governed update failed',failures,powershell=True): return
        assert_true(agents.read_text(encoding='utf-8-sig')==first_agents and manifest.read_text(encoding='utf-8-sig')==first_manifest,'Windows update is not content-idempotent',failures)
        assert_true(any(target.glob('AGENTS.md.governance-backup-*')) and any(target.glob('project-governance.yml.governance-backup-*')),'Windows update did not create backups',failures)
        legacy=parent/'Legacy'; copy_template_project(legacy)
        legacy_manifest=legacy/'project-governance.yml'
        legacy_text=legacy_manifest.read_text(encoding='utf-8-sig').replace(f'baseline: "{VERSION}"','baseline: "0.4.0"',1)
        legacy_text=re.sub(r'(?ms)^# Governed architecture-significant technology state\.\n# Allowed states:.*?^platforms:', 'platforms:', legacy_text, count=1)
        legacy_text=legacy_text.replace('  languages: []','  languages: ["PROJECT_KEEP"]',1)
        legacy_manifest.write_text(legacy_text,encoding='utf-8')
        legacy_up=run([ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'scripts/update-governed-project.ps1'),'-ProjectRoot',str(legacy),'-Apply'])
        if not command_ok(legacy_up,'Windows legacy governed update failed',failures,powershell=True): return
        legacy_updated=legacy_manifest.read_text(encoding='utf-8-sig')
        legacy_state,legacy_record=technology_baseline(legacy_updated)
        assert_true(f'baseline: "{VERSION}"' in legacy_updated,'Windows legacy update did not repin governance baseline',failures)
        assert_true(legacy_state=='RECONCILIATION_REQUIRED' and legacy_record=='docs/design.md#technology-baseline','Windows legacy update did not add Technology Baseline reconciliation state/pointer',failures)
        assert_true('languages: ["PROJECT_KEEP"]' in legacy_updated,'Windows legacy update overwrote project-owned manifest content',failures)
        adopt_clean=base/'existing-clean'; adopt_clean.mkdir(); (adopt_clean/'keep.txt').write_text('v1'); (adopt_clean/'AGENTS.md').write_text('# Project instructions\n\nADOPT_KEEP\n')
        run(['git','init'],cwd=adopt_clean); run(['git','config','user.email','gov@example.invalid'],cwd=adopt_clean); run(['git','config','user.name','Gov'],cwd=adopt_clean); run(['git','add','.'],cwd=adopt_clean); run(['git','commit','-m','base'],cwd=adopt_clean)
        adopted=run([ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'scripts/manage-governed-project.ps1'),'-Mode','Adopt','-ProjectRoot',str(adopt_clean),'-NoGitInit','-Apply'])
        if not command_ok(adopted,'Windows Adopt clean repository failed',failures,powershell=True): return
        adopted_text=(adopt_clean/'project-governance.yml').read_text(encoding='utf-8-sig')
        adopted_state,_=technology_baseline(adopted_text)
        assert_true(adopted_state=='RECONCILIATION_REQUIRED' and 'adoption:\n  state: "RECONCILIATION_REQUIRED"' in adopted_text,'Windows Adopt did not require Technology Baseline reconciliation',failures)
        adopted_agents=(adopt_clean/'AGENTS.md').read_text(encoding='utf-8-sig')
        assert_true('ADOPT_KEEP' in adopted_agents,'Windows Adopt overwrote project-owned AGENTS text',failures)
        assert_managed_template(adopted_agents,'Windows Adopt',failures)
        adopt=base/'existing'; adopt.mkdir(); (adopt/'keep.txt').write_text('v1')
        run(['git','init'],cwd=adopt); run(['git','config','user.email','gov@example.invalid'],cwd=adopt); run(['git','config','user.name','Gov'],cwd=adopt); run(['git','add','.'],cwd=adopt); run(['git','commit','-m','base'],cwd=adopt); (adopt/'keep.txt').write_text('dirty')
        bad=run([ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'scripts/manage-governed-project.ps1'),'-Mode','Adopt','-ProjectRoot',str(adopt),'-NoGitInit','-Apply'])
        assert_true(bad.returncode!=0 and not (adopt/'project-governance.yml').exists(),'Windows Adopt accepted dirty Git worktree',failures)
        bs=run([ps,'-NoProfile','-NonInteractive','-File',str(ROOT/'scripts/bootstrap-assurance.ps1'),'-ProjectRoot',str(target)])
        command_ok(bs,'Windows assurance bootstrap wrapper failed',failures,powershell=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['common','posix','windows','auto'],default='auto'); args=ap.parse_args(); failures=[]
    modes=[args.mode] if args.mode!='auto' else ['common','windows' if os.name=='nt' else 'posix']
    for mode in modes:
        if mode=='common': test_common(failures)
        elif mode=='posix': test_posix(failures)
        else: test_windows(failures)
    if failures:
        print('Framework lifecycle regression: FAIL'); [print('- '+x) for x in failures]; return 1
    print('Framework lifecycle regression: PASS ('+', '.join(modes)+')')
    print('- dry-run/non-mutation, authoritative managed-block propagation across New/Adopt/update, required-control/emergency response-completeness contracts, candidate package/apply/local validation tooling, frozen-baseline activation dry-run/apply/rollback, update idempotence, Technology Baseline migration, project-text preservation, backups, dirty-Git refusal, and host-native lifecycle paths')
    return 0
if __name__=='__main__': raise SystemExit(main())
