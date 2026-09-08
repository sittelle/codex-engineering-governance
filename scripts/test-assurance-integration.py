#!/usr/bin/env python3
import json, os, shutil, stat, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'assurance/run-verification.py'; BASELINE=ROOT/'assurance/capability-baseline.json'; AGG=ROOT/'assurance/aggregate-verification.py'
CI_RUNNER=ROOT/'assurance/run-ci-verification.py'; FIXTURE=ROOT/'tests/assurance/integration-project'; BOOTSTRAP=ROOT/'scripts/bootstrap-assurance.py'
def run(cmd,cwd=None,env=None): return subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,check=False,env=env)
def full(project,plan='verification-plan.json',report=None,context=None):
    cmd=[sys.executable,str(RUNNER),'full','--project-root',str(project),'--plan',plan,'--baseline',str(BASELINE)]
    if report: cmd+=['--report',str(report)]
    if context: cmd+=['--execution-context',context]
    return run(cmd)
def materialize_fixture(project):
    shutil.copytree(FIXTURE,project)
    p=project/'verification-plan.json'; d=json.loads(p.read_text())
    for c in d['checks']:
        cmd=c.get('command') or []
        if cmd and cmd[0]=='__TEST_PYTHON__': cmd[0]=sys.executable
    p.write_text(json.dumps(d,indent=2)+'\n')
def resolved_inventory_plan(command,execution=None,result_policy=None):
    caps=[]; required={'lint-format','type-compile','tests','build-package','secret-scan','sast'}; all_caps=[c['id'] for c in json.loads(BASELINE.read_text())['capabilities']]
    for cid in all_caps:
        if cid in required: caps.append({'id':cid,'decision':'REQUIRED','reason':'fixture baseline','checks':['gate']})
        else: caps.append({'id':cid,'decision':'OPTIONAL','reason':'fixture resolves conditional capability as optional','checks':[]})
    check={'id':'gate','stages':['quick','full'],'command':command,'reason':'fixture','timeout_seconds':10,'working_directory':None,'environment':{},'verified_targets':[]}
    if execution: check['execution']=execution
    if result_policy: check['result_policy']=result_policy
    return {'schema_version':'2','project':'execution-fixture','assurance':{'maturity':'M1','level':'SA1','facts':{'has_dependencies':False,'has_exposed_web_surface':False,'has_container_artifact':False,'has_iac':False,'has_persisted_data':False,'ships_distributable_artifact':False},'capabilities':caps},'checks':[check]}

def resolved_inventory_plan_v3(command, required_targets, result_policy=None):
    plan=resolved_inventory_plan(
        command,
        execution={
            'allowed_contexts':['CI'],
            'required_contexts':sorted({t['context'] for t in required_targets}),
            'required_targets':required_targets,
        },
        result_policy=result_policy,
    )
    plan['schema_version']='3'
    plan['project']='target-aware-execution-fixture'
    return plan

def normalized_host_target(context='CI'):
    import platform
    os_name=platform.system()
    if os_name.lower().startswith('win'):
        os_name='Windows'
    elif os_name.lower()=='linux':
        os_name='Linux'
    elif os_name.lower() in {'darwin','macos'}:
        os_name='Darwin'
    machine=platform.machine().strip().lower()
    if machine in {'amd64','x86_64','x64'}:
        machine='x86_64'
    elif machine in {'arm64','aarch64'}:
        machine='arm64'
    return {'context':context,'os':os_name,'machine':machine}

def init_git(project):
    run(['git','init'],cwd=project); run(['git','config','user.email','gov@example.invalid'],cwd=project); run(['git','config','user.name','Governance Test'],cwd=project); run(['git','config','commit.gpgSign','false'],cwd=project); run(['git','add','.'],cwd=project); return run(['git','commit','-m','fixture'],cwd=project)
def create_path_probe(tool_dir):
    if os.name=='nt':
        p=tool_dir/'gov-fake-tool.cmd'; p.write_text('@echo off\r\nexit /b 0\r\n'); return 'gov-fake-tool'
    p=tool_dir/'gov-fake-tool'; p.write_text('#!/bin/sh\nexit 0\n'); p.chmod(p.stat().st_mode|stat.S_IXUSR); return 'gov-fake-tool'
def main():
    failures=[]
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'project'; materialize_fixture(project); report=project/'.governance/evidence/full.json'
        q=run([sys.executable,str(RUNNER),'quick','--project-root',str(project),'--plan','verification-plan.json','--baseline',str(BASELINE)]); f=full(project,report=report)
        if q.returncode!=0 or 'OVERALL: PASS' not in q.stdout: failures.append('quick did not PASS')
        if f.returncode!=0 or 'OVERALL: PASS' not in f.stdout: failures.append('full did not PASS')
        if not report.exists(): failures.append('report missing')
        else:
            r=json.loads(report.read_text())
            for k in ('plan_sha256','assurance_baseline_sha256','runner_sha256','artifact_identities','capability_preflight','execution_context','required_check_ids','environment','results'):
                if k not in r: failures.append('report missing '+k)
        d=json.loads((project/'verification-plan.json').read_text()); d['assurance']['capabilities']=[c for c in d['assurance']['capabilities'] if c['id']!='sast']; d['checks']=[c for c in d['checks'] if c['id']!='sast']; (project/'omitted.json').write_text(json.dumps(d)); omitted=full(project,'omitted.json')
        if omitted.returncode!=2 or 'OVERALL: INCOMPLETE_ASSURANCE' not in omitted.stdout: failures.append('omitted required capability did not become incomplete')
        d=json.loads((project/'verification-plan.json').read_text()); next(c for c in d['checks'] if c['id']=='sast')['command']=['__definitely_missing_governance_tool__']; (project/'missing-tool.json').write_text(json.dumps(d)); missing=full(project,'missing-tool.json')
        if missing.returncode!=2 or 'DID_NOT_EXECUTE' not in missing.stdout: failures.append('missing tool semantics regressed')
        tool_dir=project/'toolbin'; tool_dir.mkdir(); probe=create_path_probe(tool_dir); d=json.loads((project/'verification-plan.json').read_text()); lint=next(c for c in d['checks'] if c['id']=='lint'); lint['command']=[probe]; lint['environment']={'PATH':str(tool_dir)+os.pathsep+os.environ.get('PATH','')}; (project/'resolver.json').write_text(json.dumps(d)); rr=run([sys.executable,str(RUNNER),'quick','--project-root',str(project),'--plan','resolver.json','--baseline',str(BASELINE),'--report',str(project/'resolver-report.json')])
        if rr.returncode!=0: failures.append('PATH resolution failed on '+os.name)
    with tempfile.TemporaryDirectory() as td:
        project=Path(td); cmd=[sys.executable,'-c','raise SystemExit(2)']; standard=resolved_inventory_plan(cmd); (project/'standard.json').write_text(json.dumps(standard)); s=full(project,'standard.json')
        if s.returncode!=1 or '-> FAIL' not in s.stdout or 'OVERALL: FAIL' not in s.stdout: failures.append('STANDARD nonzero was not FAIL')
        documented=resolved_inventory_plan(cmd,result_policy={'mode':'DOCUMENTED_EXIT_CODES','did_not_execute_codes':[2],'reference':'fixture scanner contract: 2 = operational error'}); (project/'documented.json').write_text(json.dumps(documented)); d=full(project,'documented.json')
        if d.returncode!=2 or 'DID_NOT_EXECUTE' not in d.stdout or 'OVERALL: INCOMPLETE_ASSURANCE' not in d.stdout: failures.append('documented operational code not incomplete')
        bad=resolved_inventory_plan(cmd,result_policy={'mode':'DOCUMENTED_EXIT_CODES','did_not_execute_codes':[0,2],'reference':'invalid'}); (project/'bad.json').write_text(json.dumps(bad)); b=full(project,'bad.json')
        if b.returncode!=3: failures.append('unsafe result policy accepted')
    # Approved environment + aggregation uses committed project-local artifacts.
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'repo'
        project.mkdir()
        managed=project/'.governance'
        managed.mkdir()
        shutil.copy2(RUNNER,managed/'run-verification.py')
        shutil.copy2(AGG,managed/'aggregate-verification.py')
        shutil.copy2(BASELINE,managed/'assurance-baseline.json')
        project_runner=managed/'run-verification.py'
        project_agg=managed/'aggregate-verification.py'
        project_baseline=managed/'assurance-baseline.json'
        plan=resolved_inventory_plan(
            [sys.executable,'-c','raise SystemExit(0)'],
            execution={'allowed_contexts':['CI'],'required_contexts':['CI']})
        (project/'verification-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
        init_git(project)

        def project_full(report,context):
            return run([sys.executable,str(project_runner),'full','--project-root',str(project),
                        '--plan','verification-plan.json','--baseline',str(project_baseline),
                        '--report',str(report),'--execution-context',context])

        local_report=Path(td)/'local.json'
        ci_report=Path(td)/'ci.json'
        l=project_full(local_report,'LOCAL')
        c=project_full(ci_report,'CI')

        if l.returncode!=2 or 'DEFERRED' not in local_report.read_text() or 'OVERALL: INCOMPLETE_ASSURANCE' not in l.stdout:
            failures.append('local deferral did not remain incomplete')
        if c.returncode!=0 or 'OVERALL: PASS' not in c.stdout:
            failures.append('CI required-context execution did not pass')

        ci_data=json.loads(ci_report.read_text())
        for artifact in ('plan','assurance_baseline','runner'):
            ident=ci_data.get('artifact_identities',{}).get(artifact,{})
            if ident.get('source')!='GIT_HEAD':
                failures.append(f'{artifact} identity was not commit-bound')

        a=run([sys.executable,str(project_agg),str(local_report),str(ci_report)])
        if a.returncode!=0 or 'EVIDENCE BUNDLE: PASS' not in a.stdout:
            failures.append('matching evidence did not aggregate PASS')

        # An attributable FAIL in one approved context must dominate a PASS in another
        # and must be visible in both console and machine-readable aggregate evidence.
        fail_ci=Path(td)/'ci-fail.json'
        fail_data=json.loads(ci_report.read_text())
        gate=next(x for x in fail_data['results'] if x.get('id')=='gate')
        gate['result']='FAIL'; gate['exit_code']=1; gate['execution_disposition']='COMPLETED_WITH_FAILURE'; fail_data['overall']='FAIL'
        fail_ci.write_text(json.dumps(fail_data,indent=2)+'\n',encoding='utf-8')
        fail_bundle=Path(td)/'fail-bundle.json'
        af=run([sys.executable,str(project_agg),str(local_report),str(fail_ci),'--output',str(fail_bundle)])
        if af.returncode!=1 or 'EVIDENCE BUNDLE: FAIL' not in af.stdout or 'gate FAILED in CI' not in af.stdout:
            failures.append('cross-context FAIL was not dominant and visible in console aggregation')
        else:
            fb=json.loads(fail_bundle.read_text())
            row=next((x for x in fb.get('required_checks',[]) if x.get('id')=='gate'),{})
            if row.get('status')!='FAIL' or 'CI' not in (row.get('fail_contexts') or []) or not row.get('failures'):
                failures.append('aggregate bundle did not retain contextual FAIL evidence')

        (project/'dirty.txt').write_text('dirty')
        dirty_report=Path(td)/'dirty.json'
        project_full(dirty_report,'CI')
        ad=run([sys.executable,str(project_agg),str(ci_report),str(dirty_report)])
        if ad.returncode!=2 or 'clean worktree' not in ad.stdout:
            failures.append('dirty evidence was not rejected')

        run(['git','add','dirty.txt'],cwd=project)
        run(['git','commit','-m','second'],cwd=project)
        second=Path(td)/'second.json'
        project_full(second,'CI')
        am=run([sys.executable,str(project_agg),str(ci_report),str(second)])
        if am.returncode!=2 or 'git_commit differs' not in am.stdout:
            failures.append('commit mismatch was not rejected')

    # Verification-plan v3 / report v5 target-aware execution and aggregation.
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'target-repo'
        project.mkdir()
        managed=project/'.governance'
        managed.mkdir()
        shutil.copy2(RUNNER,managed/'run-verification.py')
        shutil.copy2(AGG,managed/'aggregate-verification.py')
        shutil.copy2(BASELINE,managed/'assurance-baseline.json')
        project_runner=managed/'run-verification.py'
        project_agg=managed/'aggregate-verification.py'
        project_baseline=managed/'assurance-baseline.json'

        host=normalized_host_target('CI')
        other_os='Windows' if host['os']!='Windows' else 'Linux'
        other={'context':'CI','os':other_os,'machine':'x86_64'}
        host_required={'context':'CI','os':host['os'],'machine':host['machine']}
        targets=[host_required,other]
        plan=resolved_inventory_plan_v3([sys.executable,'-c','raise SystemExit(0)'],targets)
        (project/'verification-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
        init_git(project)

        host_report=Path(td)/'host-v5.json'
        r=run([sys.executable,str(project_runner),'full','--project-root',str(project),
               '--plan','verification-plan.json','--baseline',str(project_baseline),
               '--report',str(host_report),'--execution-context','CI'])
        if r.returncode!=2 or 'OVERALL: INCOMPLETE_ASSURANCE' not in r.stdout:
            failures.append('v3 single-target report did not remain incomplete for missing peer target')
        if not host_report.exists():
            failures.append('v3 runner did not emit report v5')
        else:
            hd=json.loads(host_report.read_text())
            if hd.get('schema_version')!='5' or hd.get('plan_schema_version')!='3':
                failures.append('v3 runner did not emit report schema v5')
            if hd.get('execution_target')!=host:
                failures.append('v5 execution_target was not derived from host/context')
            gate=next((x for x in hd.get('results',[]) if x.get('id')=='gate'),{})
            if gate.get('result')!='PASS' or gate.get('target_match')!='MATCH' or gate.get('actual_target')!=host:
                failures.append('v3 matching target did not execute as PASS/MATCH')

            # Clone the clean attributable report only as a synthetic aggregator fixture for
            # the second OS target. The aggregator must distinguish same-context CI targets.
            peer=Path(td)/'peer-v5.json'
            pd=json.loads(host_report.read_text())
            pd['execution_target']=other
            pd['environment']['os']=other['os']; pd['environment']['machine']=other['machine']; pd['environment']['release']='synthetic-test'
            # Cross-platform checkout bytes may differ (for example CRLF/LF) even when
            # the committed Git identity is identical. Keep those hashes diagnostic only.
            for identity in (pd.get('artifact_identities') or {}).values():
                if isinstance(identity,dict) and identity.get('working_tree_sha256'):
                    identity['working_tree_sha256']='f'*64
            for row in pd.get('results',[]):
                row['actual_target']=other
                if row.get('required_targets'):
                    row['target_match']='MATCH'
            peer.write_text(json.dumps(pd,indent=2)+'\n',encoding='utf-8')

            bundle=Path(td)/'target-bundle.json'
            ar=run([sys.executable,str(project_agg),str(host_report),str(peer),'--output',str(bundle)])
            if ar.returncode!=0 or 'EVIDENCE BUNDLE: PASS' not in ar.stdout:
                failures.append('v5 Windows/Linux target evidence did not aggregate PASS')
            elif bundle.exists():
                bd=json.loads(bundle.read_text())
                if bd.get('schema_version')!='2' or bd.get('report_schema_version')!='5':
                    failures.append('target-aware aggregation did not emit bundle schema v2')
                row=next((x for x in bd.get('required_checks',[]) if x.get('id')=='gate'),{})
                if row.get('status')!='PASS' or len(row.get('pass_targets') or [])<2:
                    failures.append('target-aware aggregate did not retain both PASS targets')

            canonical_mismatch=Path(td)/'peer-canonical-mismatch-v5.json'
            cmd=json.loads(peer.read_text())
            cmd['artifact_identities']['plan']['sha256']='0'*64
            canonical_mismatch.write_text(json.dumps(cmd,indent=2)+'\n',encoding='utf-8')
            cm=run([sys.executable,str(project_agg),str(host_report),str(canonical_mismatch)])
            if cm.returncode!=2 or 'canonical artifact identity differs across reports' not in cm.stdout:
                failures.append('canonical artifact identity mismatch was not rejected')

            only=run([sys.executable,str(project_agg),str(host_report)])
            if only.returncode!=2 or 'lacks required PASS evidence for target' not in only.stdout:
                failures.append('missing required target did not aggregate INCOMPLETE_ASSURANCE')

            fail_peer=Path(td)/'peer-fail-v5.json'
            fd=json.loads(peer.read_text())
            fgate=next(x for x in fd['results'] if x.get('id')=='gate')
            fgate['result']='FAIL'; fgate['exit_code']=1; fgate['execution_disposition']='COMPLETED_WITH_FAILURE'; fd['overall']='FAIL'
            fail_peer.write_text(json.dumps(fd,indent=2)+'\n',encoding='utf-8')
            af=run([sys.executable,str(project_agg),str(host_report),str(fail_peer)])
            if af.returncode!=1 or 'EVIDENCE BUNDLE: FAIL' not in af.stdout or other['os'] not in af.stdout:
                failures.append('target-specific FAIL was not dominant/visible')

            # Historical report v4 cannot be mixed with v5 target-aware evidence.
            v2plan=resolved_inventory_plan([sys.executable,'-c','raise SystemExit(0)'])
            (project/'v2.json').write_text(json.dumps(v2plan,indent=2)+'\n',encoding='utf-8')
            run(['git','add','v2.json'],cwd=project); run(['git','commit','-m','v2-plan'],cwd=project)
            v4=Path(td)/'legacy-v4.json'
            legacy=run([sys.executable,str(project_runner),'full','--project-root',str(project),
                        '--plan','v2.json','--baseline',str(project_baseline),
                        '--report',str(v4),'--execution-context','CI'])
            if legacy.returncode!=0 or json.loads(v4.read_text()).get('schema_version')!='4':
                failures.append('v2 compatibility did not retain report v4')
            mixed=run([sys.executable,str(project_agg),str(host_report),str(v4)])
            if mixed.returncode!=3 or 'mixed report schema versions' not in (mixed.stdout+mixed.stderr):
                failures.append('mixed v4/v5 evidence was not rejected')

        # A v3 target mismatch is explicit nonexecution, never a hidden skip.
        mismatch_plan=resolved_inventory_plan_v3([sys.executable,'-c','raise SystemExit(0)'],[other])
        (project/'mismatch.json').write_text(json.dumps(mismatch_plan,indent=2)+'\n',encoding='utf-8')
        mismatch_report=Path(td)/'mismatch-v5.json'
        mm=run([sys.executable,str(project_runner),'full','--project-root',str(project),
                '--plan','mismatch.json','--baseline',str(project_baseline),
                '--report',str(mismatch_report),'--execution-context','CI'])
        if mm.returncode!=2 or not mismatch_report.exists():
            failures.append('target mismatch did not become incomplete assurance')
        else:
            md=json.loads(mismatch_report.read_text())
            gate=next((x for x in md.get('results',[]) if x.get('id')=='gate'),{})
            if gate.get('result')!='DID_NOT_EXECUTE' or gate.get('execution_disposition')!='ENVIRONMENT_MISMATCH' or gate.get('target_match')!='MISMATCH':
                failures.append('target mismatch semantics are not DID_NOT_EXECUTE/ENVIRONMENT_MISMATCH')

        invalid_plan=resolved_inventory_plan_v3([sys.executable,'-c','raise SystemExit(0)'],[host_required])
        invalid_plan['checks'][0]['execution']['required_contexts']=['ANY']
        (project/'invalid-target.json').write_text(json.dumps(invalid_plan,indent=2)+'\n',encoding='utf-8')
        invalid=run([sys.executable,str(project_runner),'full','--project-root',str(project),
                     '--plan','invalid-target.json','--baseline',str(project_baseline),'--execution-context','CI'])
        if invalid.returncode!=3:
            failures.append('v3 ANY + required_targets ambiguity was accepted')

    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'bootstrap'; project.mkdir(); shutil.copy2(ROOT/'templates/repository/project-governance.yml',project/'project-governance.yml'); shutil.copy2(ROOT/'templates/repository/.gitignore',project/'.gitignore'); mat=Path(td)/'mat'; materialize_fixture(mat); shutil.copy2(mat/'verification-plan.json',project/'verification-plan.json'); b=run([sys.executable,str(BOOTSTRAP),'--project-root',str(project),'--apply'])
        if b.returncode!=0: failures.append('bootstrap failed: '+b.stderr)
        for rel in ['.governance/run-verification.py','.governance/run-ci-verification.py','.governance/aggregate-verification.py','.governance/assurance-baseline.json','.governance/assurance-bootstrap.json','.github/workflows/governance-verify.yml']:
            if not (project/rel).exists(): failures.append('bootstrap missing '+rel)
        wf=project/'.github/workflows/governance-verify.yml'
        if wf.exists() and '.governance/run-ci-verification.py' not in wf.read_text(): failures.append('workflow lacks managed CI verification orchestrator')

    # CI orchestrator must emit incomplete-assurance evidence even when bootstrap fails.
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'ci-orchestrator'
        project.mkdir()
        materialized=Path(td)/'materialized-ci-fixture'
        materialize_fixture(materialized)
        shutil.copy2(materialized/'verification-plan.json',project/'verification-plan.json')
        (project/'.governance').mkdir(parents=True)
        shutil.copy2(RUNNER,project/'.governance/run-verification.py')
        shutil.copy2(BASELINE,project/'.governance/assurance-baseline.json')
        shutil.copy2(CI_RUNNER,project/'.governance/run-ci-verification.py')
        init_git(project)
        # Commit managed identity artifacts before executing.
        run(['git','add','.'],cwd=project); run(['git','commit','-m','managed'],cwd=project)
        bootstrap=project/'.governance/ci-bootstrap.py'
        bootstrap.write_text('raise SystemExit(7)\n',encoding='utf-8')
        run(['git','add','.governance/ci-bootstrap.py'],cwd=project); run(['git','commit','-m','bootstrap'],cwd=project)
        report=project/'.governance/evidence/ci-full.json'
        cr=run([sys.executable,str(project/'.governance/run-ci-verification.py'),'--project-root',str(project),'--plan','verification-plan.json','--baseline','.governance/assurance-baseline.json','--report',str(report)],cwd=project)
        if cr.returncode!=2:
            failures.append('failed CI bootstrap did not return incomplete-assurance exit')
        if not report.exists():
            failures.append('failed CI bootstrap did not emit ci-full report')
        else:
            rr=json.loads(report.read_text())
            if rr.get('overall')!='INCOMPLETE_ASSURANCE' or not rr.get('precondition_failure'):
                failures.append('failed CI bootstrap report missing precondition incomplete assurance')
            if not any(x.get('execution_disposition')=='PRECONDITION_FAILURE' for x in rr.get('results',[])):
                failures.append('failed CI bootstrap did not mark checks PRECONDITION_FAILURE')

    if failures:
        print('Assurance integration: FAIL'); [print('- '+x) for x in failures]; return 1
    print('Assurance integration: PASS'); print('- host-neutral fixture interpreter materialization'); print('- host-appropriate PATH-resolution probe'); print('- prior capability completeness and executable resolution preserved'); print('- STANDARD nonzero => FAIL'); print('- documented operational exit => DID_NOT_EXECUTE / INCOMPLETE_ASSURANCE'); print('- unsafe result policy rejected'); print('- approved execution-context deferral'); print('- commit/plan/baseline/runner-bound evidence aggregation'); print('- attributable FAIL dominates cross-context PASS and is visible in aggregate evidence'); print('- dirty and mismatched-commit evidence rejected'); print('- project bootstrap installs runner, CI orchestrator, aggregator, baseline, and CI context'); print('- failed CI bootstrap => attributable DID_NOT_EXECUTE / INCOMPLETE_ASSURANCE report'); print('- verification-plan v3 derives trusted execution targets and emits report v5'); print('- target mismatch => DID_NOT_EXECUTE / ENVIRONMENT_MISMATCH'); print('- target-aware aggregation requires every required target and emits bundle v2'); print('- cross-platform working-tree hashes remain diagnostic while canonical Git artifact identity is enforced'); print('- target-specific FAIL remains dominant and visible'); print('- v2/report-v4 compatibility preserved and mixed v4/v5 aggregation rejected'); return 0
if __name__=='__main__': raise SystemExit(main())
