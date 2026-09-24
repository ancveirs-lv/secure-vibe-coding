#!/usr/bin/env python3
"""Offline synthetic contract checks against the published v0.1.1 evaluator."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PILOT=Path(__file__).resolve().parent
ROOT=PILOT.parents[1]
PROTOCOL=json.loads((PILOT/'protocol.json').read_text(encoding='utf8'))
BASELINE_SHA=PROTOCOL['baseline_commit']
LANGS=('en','lv')


def load(path:Path):
    return json.loads(path.read_text(encoding='utf8'))


def invoke(payload:Path,lang='en',flag=None):
    cmd=[sys.executable,str(ROOT/'scripts/assess.py'),str(payload),'--lang',lang]
    if flag:
        cmd.append(flag)
    return subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=15)


def invoke_fixture(payload:Path,lang='en',flag=None):
    data=load(payload)
    assessment_input={key:data[key] for key in ('assessment_id','version','answers')}
    with tempfile.TemporaryDirectory(prefix='svc-pilot001-fixture-') as tmp:
        clean=Path(tmp)/'assessment.json'
        clean.write_text(json.dumps(assessment_input,ensure_ascii=False),encoding='utf8')
        return invoke(clean,lang,flag)


def insist(condition,message):
    if not condition:
        raise AssertionError(message)


def check_model():
    for path,sha in PROTOCOL['pinned_input_sha256'].items():
        actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        insist(actual==sha,f'pinned v0.1.1 input drift: {path}')
    meta=load(ROOT/'data/meta.json')
    en=load(ROOT/'data/assessment.en.json')
    lv=load(ROOT/'data/assessment.lv.json')
    insist(meta['version']==PROTOCOL['baseline_assessment_version'],'baseline version drift')
    insist(meta['assessment_id']=='SVC','assessment identity drift')
    insist(meta['expected_item_count']==32,'count drift')
    insist(meta['expected_domain_count']==8,'domain drift')
    insist(meta['expected_slop_indicator_count']==16,'indicator drift')
    insist(len(en['items'])==len(lv['items'])==32,'invalid bilingual count')
    ids=[x['id'] for x in en['items']]
    insist(len(set(ids))==32,'duplicate canonical control ids')
    insist(ids==[x['id'] for x in lv['items']],'language control id mismatch')
    assert_fields=('domain','required_state','release_blocking','na_allowed','source_refs')
    for e,l in zip(en['items'],lv['items']):
        for f in assert_fields:
            insist(e[f]==l[f],f'EN/LV semantic mismatch {e["id"]} {f}')
    return ids,meta,en


def checks():
    ids,meta,en=check_model()
    expected=PROTOCOL['expected_gates']
    observed=[]
    exit_cases=[]
    fixture_hashes={}
    for name,want in expected.items():
        fp=PILOT/'fixtures'/f'{name}.json'
        fixture_hashes[name]=hashlib.sha256(fp.read_bytes()).hexdigest()
        data=load(fp)
        insist(data['assessment_id']=='SVC' and data['version']==meta['version'],f'{name} baseline mismatch')
        insist(data.get('scenario_id')==name,f'{name}: case identity mismatch')
        insist(set(data['answers'])==set(ids),f'{name}: fixture must explicitly cover all 32 controls')
        for x in data['answers'].values():
            if x['state']=='VERIFIED':
                insist(x['evidence'].startswith('SYNTHETIC TEST TOKEN'),f'{name}: misleading demonstration evidence label')
        lang_outputs={}
        for lang in LANGS:
            proc=invoke_fixture(fp,lang)
            insist(proc.returncode==0,f'{name} {lang} CLI error: {proc.stderr or proc.stdout}')
            out=json.loads(proc.stdout)
            insist(out['gate']==want,f'{name} {lang} gate {out["gate"]} != {want}')
            insist(out['version']==meta['version'] and out['language']==lang,f'{name} output contract mismatch')
            insist(len(out['all_gaps'])==len({x['id'] for x in out['all_gaps']}),f'{name}: repeated gap ids')
            insist(not any(k.lower() in ('score','security_score','compliance_score','maturity_score') for k in out),f'{name}: prohibited score')
            insist('not validated automatically' in out['note'],f'{name}: missing evidence caveat')
            lang_outputs[lang]=out
            for flag,expect_status in (
                ('--fail-on-blocked',2 if want=='BLOCKED' else 0),
                ('--require-ready',0 if want=='READY' else 2),
            ):
                gated=invoke_fixture(fp,lang,flag)
                insist(gated.returncode==expect_status,f'{name} {lang} {flag} exit={gated.returncode} expected={expect_status}: {gated.stderr}')
                insist(json.loads(gated.stdout)['gate']==want,f'{name} {flag} altered gate')
                exit_cases.append({'scenario':name,'language':lang,'mode':flag,'expected_exit':expect_status,'observed_exit':gated.returncode})
        a,b=lang_outputs['en'],lang_outputs['lv']
        for key in ('gate','overall_state_counts','unknown_items','not_applicable_items'):
            insist(a[key]==b[key],f'{name}: EN/LV output mismatch in {key}')
        def gap_ids(obj,key):return [g['id'] for g in obj[key]]
        insist(gap_ids(a,'all_gaps')==gap_ids(b,'all_gaps'),f'{name}: EN/LV gap mismatch')
        insist(gap_ids(a,'blocking_gaps')==gap_ids(b,'blocking_gaps'),f'{name}: EN/LV blockers mismatch')
        if name=='blocked':
            insist(sorted(gap_ids(a,'blocking_gaps'))==sorted(PROTOCOL['expected_blocking_ids']),'unexpected blocking controls')
            insist('O03' in gap_ids(a,'all_gaps'),'expected non-blocking gap missing')
        elif name=='conditional':
            insist(gap_ids(a,'blocking_gaps')==[],'conditional has blockers')
            insist(sorted(gap_ids(a,'all_gaps'))==sorted(PROTOCOL['expected_conditional_gap_ids']),'unexpected conditional gaps')
        else:
            insist(not a['all_gaps'] and not a['blocking_gaps'],'ready must have no structural gaps')
        observed.append({
            'id':name,'expected_gate':want,'observed_gate_en':a['gate'],'observed_gate_lv':b['gate'],
            'blocking_ids':gap_ids(a,'blocking_gaps'),'gap_ids':gap_ids(a,'all_gaps'),
            'state_counts':a['overall_state_counts'],'complete_control_coverage':True,
            'fixture_sha256':fixture_hashes[name]
        })

    payload=load(PILOT/'fixtures'/'ready.json')
    assessment_payload={key:payload[key] for key in ('assessment_id','version','answers')}
    negative=[
        ('wrong_identity',{'assessment_id':'OTHER'},'assessment_id mismatch'),
        ('missing_identity',{'assessment_id':None},'assessment_id mismatch'),
        ('wrong_version',{'version':'0.1.0'},'version mismatch'),
        ('missing_version',{'version':None},'version mismatch'),
        ('unknown_control',{'answers':{**payload['answers'],'Z99':'VERIFIED'}},'unknown control IDs'),
        ('answers_list',{'answers':[]},'answers must be a JSON object'),
        ('verified_no_evidence',{'answers':{**payload['answers'],'O04':{'state':'VERIFIED','evidence':'   '}}},'VERIFIED requires evidence'),
        ('na_disallowed',{'answers':{**payload['answers'],'O01':{'state':'NOT_APPLICABLE','note':'testing invalid N/A'}}},'NOT_APPLICABLE is not allowed'),
        ('na_missing_reason',{'answers':{**payload['answers'],'G03':{'state':'NOT_APPLICABLE','note':' '}}},'NOT_APPLICABLE requires note'),
        ('unknown_state',{'answers':{**payload['answers'],'O01':{'state':'PASS'}}},'invalid state'),
        ('unsupported_answer_field',{'answers':{**payload['answers'],'O01':{'state':'VERIFIED','evidence':'SYNTHETIC TEST TOKEN','rating':100}}},'unsupported answer fields'),
        ('nonstring_evidence',{'answers':{**payload['answers'],'O01':{'state':'VERIFIED','evidence':123}}},'notes and evidence must be strings'),
    ]
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='svc-pilot001-') as tmp:
        for name,change,phrase in negative:
            data={**assessment_payload,**change}
            fp=Path(tmp)/f'{name}.json'
            fp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
            for lang in LANGS:
                r=invoke(fp,lang)
                insist(r.returncode!=0,f'{name} {lang}: malformed input was accepted')
                insist(phrase in (r.stderr+r.stdout),f'{name} {lang}: wrong rejection: {r.stderr+r.stdout}')
            rejected.append(name)
        bad_root=Path(tmp)/'root_array.json'
        bad_root.write_text('[]',encoding='utf8')
        for lang in LANGS:
            r=invoke(bad_root,lang)
            insist(r.returncode!=0 and 'assessment input must be a JSON object' in (r.stderr+r.stdout),'root array accepted')
        rejected.append('root_array')
        sparse=Path(tmp)/'sparse.json'
        sparse.write_text(json.dumps({'assessment_id':'SVC','version':meta['version'],'answers':{'O01':'CLAIMED'}}),encoding='utf8')
        for lang in LANGS:
            r=invoke(sparse,lang)
            insist(r.returncode==0 and json.loads(r.stdout)['gate']=='BLOCKED',f'{lang}: sparse answers bypassed block')
            r2=invoke(sparse,lang,'--fail-on-blocked')
            insist(r2.returncode==2,f'{lang}: sparse input escaped CI')

        unsupported_truth=Path(tmp)/'fabricated_notes.json'
        unsupported_truth.write_text(json.dumps(assessment_payload,ensure_ascii=False),encoding='utf8')
        a=invoke(unsupported_truth,'en','--require-ready')
        insist(a.returncode==0 and json.loads(a.stdout)['gate']=='READY','evidence authenticity limitation behaviour changed; update pilot')
        fake_na=json.loads(unsupported_truth.read_text(encoding='utf8'))
        fake_na['answers']['G03']={'state':'NOT_APPLICABLE','note':'synthetic unverified assertion'}
        unsupported_truth.write_text(json.dumps(fake_na,ensure_ascii=False),encoding='utf8')
        b=invoke(unsupported_truth,'lv','--require-ready')
        insist(b.returncode==0 and json.loads(b.stdout)['gate']=='READY','N/A justification limitation behaviour changed; update pilot')

        duplicate=Path(tmp)/'duplicate_key.json'
        original=(PILOT/'fixtures'/'ready.json').read_text(encoding='utf8')
        marker='    "O01": {'
        insist(original.count(marker)==1,'duplicate-key setup marker drift')
        duplicate.write_text(original.replace(marker,'    "O01": "UNKNOWN",\n'+marker,1),encoding='utf8')
        for lang in LANGS:
            d=invoke(duplicate,lang,'--require-ready')
            insist(d.returncode!=0 and 'duplicate JSON key rejected: O01' in (d.stderr+d.stdout),'duplicate-key remediation missing')
        rejected.append('duplicate_answer_key')
    result={
        'pilot_id':'PILOT-001','result':'PASS','baseline_version':meta['version'],
        'baseline_release':PROTOCOL['baseline_release'],'baseline_commit':BASELINE_SHA,
        'data_classification':'SYNTHETIC FIXTURES ONLY; NOT REAL PRODUCT SECURITY EVIDENCE',
        'scope':'offline release-gate and input-contract checks, not software security validation',
        'controls':32,'domains':8,'slop_indicators':16,
        'scenarios':observed,'exit_contracts':exit_cases,
        'negative_input_cases_rejected':rejected,
        'sparse_input':'BLOCKED in EN/LV; gated exit=2',
        'known_limitations':[
            {'id':'LIM-EVIDENCE-001','observed':'Fabricated nonempty evidence strings are accepted and can yield READY. Evidence authenticity is not established.'},
            {'id':'LIM-APPLICABILITY-002','observed':'A nonempty NOT_APPLICABLE reason is accepted where N/A is allowed; semantic truth is not verified.'},
            {'id':'LIM-DUPLICATE-003','observed':'Historical PILOT-001 finding: duplicate JSON answer keys were last-wins in the published v0.1.1 evaluator. INPUT-001 now rejects duplicates fail-closed.','status':'REMEDIATED'},
            {'id':'LIM-SYNTHETIC-004','observed':'No real product, security tooling output or independently authenticated evidence was assessed.'},
        ],
        'release_claim':'Structural decision-contract validation only; no production safety or compliance conclusion.',
    }
    return result


def markdown(data,lang):
    if lang=='en':
        lines=['# PILOT-001 — Synthetic release-gate results','','**Outcome: PASS for structural CLI behaviour only.** No real product was assessed.','',
            f'Baseline: `{data["baseline_release"]}` at `{data["baseline_commit"]}`; 32 controls, eight domains, 16 diagnostic indicators.','',
            '| Scenario | Expected | Observed EN | Observed LV | Blocking gaps | Total gaps |',
            '| --- | --- | --- | --- | ---: | ---: |']
        for x in data['scenarios']:
            lines.append(f'| `{x["id"]}` | `{x["expected_gate"]}` | `{x["observed_gate_en"]}` | `{x["observed_gate_lv"]}` | {len(x["blocking_ids"])} | {len(x["gap_ids"])} |')
        lines.extend(['',f'Invalid input contracts rejected: **{len(data["negative_input_cases_rejected"])}** vectors in both languages.',
            f'CI exit contracts verified: **{len(data["exit_contracts"])}** combinations.',
            'Incomplete answers fail the release-blocking gate (`BLOCKED`).','',
            '## Deliberately exposed limitations','',
            '- **LIM-EVIDENCE-001:** fabricated nonempty evidence strings can produce `READY`. The tool checks presence, **not evidence authenticity**.',
            '- **LIM-APPLICABILITY-002:** when N/A is allowed, a nonempty reason is accepted without verifying its factual basis.',
            '- **LIM-DUPLICATE-003 — REMEDIATED by INPUT-001:** the original last-wins finding remains historical; the current evaluator rejects duplicate JSON keys.',
            '- **LIM-SYNTHETIC-004:** fixture scenarios do not test or establish the security of any real product.','',
            '**Interpretation:** `READY` here demonstrates the evaluator’s formal decision contract, not permission to deploy software.',''])
    else:
        lines=['# PILOT-001 — Sintētiskā izmēģinājuma rezultāti','','**Rezultāts: PASS tikai strukturētajai CLI darbībai.** Nav pārbaudīts neviens reāls produkts.','',
            f'Pamats: `{data["baseline_release"]}` commit `{data["baseline_commit"]}`; 32 kontroles, astoņas jomas un 16 diagnostiski indikatori.','',
            '| Scenārijs | Sagaidāmais | EN rezultāts | LV rezultāts | Bloķējošās nepilnības | Visas nepilnības |',
            '| --- | --- | --- | --- | ---: | ---: |']
        for x in data['scenarios']:
            lines.append(f'| `{x["id"]}` | `{x["expected_gate"]}` | `{x["observed_gate_en"]}` | `{x["observed_gate_lv"]}` | {len(x["blocking_ids"])} | {len(x["gap_ids"])} |')
        lines.extend(['',f'Noraidīti **{len(data["negative_input_cases_rejected"])}** kļūdainas ievades vektori abās valodās.',
            f'Pārbaudītas **{len(data["exit_contracts"])}** CI atgriešanās kodu kombinācijas.',
            'Nepilnīgas atbildes bloķē izlaišanu (`BLOCKED`).','',
            '## Apzināti fiksētie ierobežojumi','',
            '- **LIM-EVIDENCE-001:** izdomātas, netukšas pierādījumu virknes var radīt `READY`. Rīks pārbauda **esamību, nevis patiesumu**.',
            '- **LIM-APPLICABILITY-002:** tur, kur atļauts N/A, netukšs pamatojums tiek pieņemts bez faktu pārbaudes.',
            '- **LIM-DUPLICATE-003 — REMEDIATED ar INPUT-001:** sākotnējais last-wins atradums paliek vēsturiskajā ierakstā; pašreizējais evaluators noraida atkārtotas JSON atslēgas.',
            '- **LIM-SYNTHETIC-004:** scenāriji nepierāda neviena reāla produkta drošību.','',
            '**Interpretācija:** `READY` šajā izmēģinājumā pierāda formālu novērtēšanas loģiku, nevis atļauju izvietot programmatūru.',''])
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser()
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check',action='store_true')
    mode.add_argument('--write',action='store_true')
    args=p.parse_args()
    try:
        data=checks()
        render={
            PILOT/'reports/results.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
            PILOT/'reports/summary.en.md':markdown(data,'en'),
            PILOT/'reports/summary.lv.md':markdown(data,'lv'),
        }
        for path,text in render.items():
            if args.write:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(text,encoding='utf8')
            else:
                insist(path.is_file() and path.read_text(encoding='utf8')==text,f'stale or missing report: {path.relative_to(ROOT)}')
    except (AssertionError,ValueError,KeyError,subprocess.TimeoutExpired) as e:
        print('PILOT-001 FAIL: '+str(e),file=sys.stderr)
        return 1
    print('PILOT-001 PASS: 3 scenarios × EN/LV; 12 CI exit checks; 14 invalid inputs × EN/LV; duplicate-key finding remediated; evidence/N/A limitations remain.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
