#!/usr/bin/env python3
"""Execute inert workflow-handoff composition checks for documented multi-skill flows."""
from __future__ import annotations
import json, tempfile, sys, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'eval-results'; FLOWS=json.loads((ROOT/'evals'/'composition'/'cases.json').read_text(encoding='utf-8'))['flows']
sys.path.insert(0, str(ROOT/'scripts'))
from workflow_state import atomic_write, update_state
REQUIRED={"schema_version","source_skill","run_status","summary","topics","findings","decisions","open_questions","recommended_actions","recommended_next_skills","full_output_file"}
def main() -> int:
    outcomes=[]
    for flow in FLOWS:
        errors=[]; state={"schema_version":"1.0","custom":{"keep":True},"runs":{}}; prior=[]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            workflow=root/'.ai-workflow'; workflow.mkdir()
            atomic_write(workflow/'state.json', json.dumps(state))
            for skill in flow['skills']:
                # Only compact matching-topic handoffs are considered; full artifacts remain unopened.
                relevant=[h for h in prior if set(h['topics']) & set(flow['topics'])]
                unrelated={"topics":["unrelated"],"findings":[],"full_output_file":"never-open.md"}
                if unrelated in relevant: errors.append(f'{skill}: consumed unrelated handoff')
                if prior and not relevant: errors.append(f'{skill}: did not select a relevant inherited handoff')
                handoff={"schema_version":"1.0","source_skill":skill,"run_status":"completed","summary":"concise verified lead","topics":flow['topics'],"findings":[{"id":skill.upper()[:4]+'-001',"related_topics":flow['topics'],"source_skill":prior[-1]['source_skill'] if prior else None}],"decisions":[],"open_questions":[],"recommended_actions":[],"recommended_next_skills":[],"full_output_file":f'.ai-workflow/artifacts/{skill}.md'}
                if not REQUIRED <= handoff.keys(): errors.append(f'{skill}: invalid handoff')
                (workflow/'artifacts').mkdir(exist_ok=True); (workflow/'handoffs').mkdir(exist_ok=True)
                atomic_write(root/handoff['full_output_file'], handoff['summary'])
                atomic_write(workflow/'handoffs'/f'{skill}.json', json.dumps(handoff))
                state,_=update_state(workflow, skill, {"status":"completed","handoff_file":f'.ai-workflow/handoffs/{skill}.json'})
                if prior and handoff['findings'][0]['source_skill'] != prior[-1]['source_skill']:
                    errors.append(f'{skill}: inherited finding provenance/re-verification failed')
                prior.append(handoff)
            if state.get('custom') != {"keep":True} or set(state['runs']) != set(flow['skills']): errors.append('state overwrite or missing run')
            if any(len(h['summary'])>200 for h in prior): errors.append('handoff context budget exceeded')
            if len(prior)>1 and not prior[-1]['findings'][0]['source_skill']: errors.append('inherited finding provenance missing')
        outcomes.append({"id":flow['id'],"status":"passed" if not errors else "failed","errors":errors})
    OUT.mkdir(exist_ok=True); (OUT/'composition-report.md').write_text('# Composition eval report\n\n'+'\n'.join(f"- {x['status'].upper()} `{x['id']}` {'; '.join(x['errors'])}" for x in outcomes)+'\n',encoding='utf-8')
    (OUT/'composition.json').write_text(json.dumps(outcomes,indent=2),encoding='utf-8')
    suite=ET.Element('testsuite',name='composition',tests=str(len(outcomes)),failures=str(sum(x['status']=='failed' for x in outcomes)))
    for outcome in outcomes:
        node=ET.SubElement(suite,'testcase',classname='composition',name=outcome['id'])
        if outcome['status']=='failed':
            ET.SubElement(node,'failure',message='; '.join(outcome['errors']))
    ET.ElementTree(suite).write(OUT/'composition-junit.xml',encoding='utf-8',xml_declaration=True)
    print(f"{'FAIL' if any(x['errors'] for x in outcomes) else 'PASS'}: {len(outcomes)} composition flows.")
    return 1 if any(x['errors'] for x in outcomes) else 0
if __name__=='__main__': raise SystemExit(main())
