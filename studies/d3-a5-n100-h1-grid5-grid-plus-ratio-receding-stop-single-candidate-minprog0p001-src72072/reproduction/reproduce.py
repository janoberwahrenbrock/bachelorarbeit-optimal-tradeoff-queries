"""One fresh publication validation; stdlib only, no solver or native phase."""
import argparse,csv,hashlib,json,sys,types
from fractions import Fraction
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=a.project_root.resolve(strict=True);out=a.output.absolute();meta=json.loads((Path(__file__).parent/'reproduction.json').read_bytes());public=root/meta['public_root'];sid=meta['study_id']
if out.exists()or out.is_symlink()or out.resolve(strict=False).is_relative_to(root):raise ValueError('Fresh analysis output outside immutable extraction required')
def read(r):
 p=root/r['path'];b=p.read_bytes()
 if p.is_symlink()or len(b)!=r['bytes']or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Published FullRef differs: '+r['path'])
 return b
def doc(r):return json.loads(read(r))
def load(r,name):
 b=read(r);m=types.ModuleType(name);m.__file__=str(root/r['path']);exec(compile(b,m.__file__,'exec'),m.__dict__);return m
def raw_core(v):return {k:x for k,x in v.items()if k not in ('created_at_utc','elapsed_seconds')}
reporter=load(meta['tools']['report'],'published_E5_report');checker=load(meta['tools']['raw'],'published_E5_raw');compare=load(meta['compare'],'published_compare')
reference=doc(meta['report']);report=reporter.analyze(root,meta['series_path'],meta['admission']);comparison=compare.compare(reference,report);raw=doc(meta['raw'])
series=root/meta['series_path'];plan=json.loads((series/'plan.json').read_bytes());state=json.loads((series/'state.json').read_bytes());finish=json.loads((root/meta['finish_proof']).read_bytes())
if meta['A3_issue']is None:
 reproduced=checker.verify_study(root,meta['series_path'],root/meta['finish_proof'],root/meta['wheel']['path'],root/meta['admission']['path'],meta['admission'])
 if reproduced['status']!='provisional_pass'or reproduced['findings']or raw_core(reproduced)!=raw_core(raw):raise ValueError('Full immutable Raw comparison differs')
else:
 issue=doc(meta['A3_issue']['result']);accepted=doc(meta['A3_issue']['Root_acceptance']);completed=doc(meta['A3_issue']['completed'])
 if raw['status']!='provisional_failed'or raw['findings']!=issue['original_findings']or issue['original_raw']!=meta['raw']or accepted['original_raw']!=meta['raw']or completed['actual_full_raw_calls']!=0:raise ValueError('A3 original failure/discharge history changed')
 # Publication validates exports only; no second full A3 Raw is called.
 checker.FILES.clear();exports=checker.verify_exports(series,plan,state,finish,raw['rows'])
 if exports!=issue['exports']:raise ValueError('A3 corrected export-only comparison differs')
def resolve(base,r):
 p=base/r['path'];b=p.read_bytes()
 if hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Native exact artifact differs')
 return json.loads(b)
correct=unsolved=answers=0
if len(plan['jobs'])!=100 or len(state['jobs'])!=100:raise ValueError('All100 primary cases required')
for j,s,row in zip(plan['jobs'],state['jobs'],report['rows']):
 if j['job_id']!=s['job_id']or len(s['attempts'])!=1:raise ValueError('Original one-attempt denominator differs')
 problem=resolve(series,j['problem']);oracle=resolve(series,j['oracle']);result=resolve(series,s['attempts'][0]['result']);sol=result['solver_result'];weights=list(map(Fraction,oracle['target_weights']));scores=[sum(Fraction(x)*w for x,w in zip(v,weights))for v in problem['alternatives']];best=max(scores);winners=[name for name,v in zip(problem['alternative_ids'],scores)if v==best]
 if result['execution_status']!='completed'or result['error']is not None:raise ValueError('Unexpected native error')
 if sol['solved']:
  if sol['selected_candidate_id']not in winners or row['quality']!='correct':raise ValueError('Saved selected winner differs')
  correct+=1
 else:
  if sol['selected_candidate_id']is not None or row['solved']:raise ValueError('Unsolved case relabeled')
  unsolved+=1
 for q in sol['answered_queries']:
  delta=weights[q['goal_index_a']]-Fraction(q['value'])*weights[q['goal_index_b']];answer='>'if delta>0 else'<'if delta<0 else'='
  if q['answer']!=answer:raise ValueError('Exact Fraction answer differs')
  answers+=1
expected=meta['expected']
if (correct,unsolved,answers)!=(expected['correct'],expected['regular_unsolved'],expected['answers']):raise ValueError('Scientific totals differ')
outputs={'results.json':reporter.encoded(report),'report.md':reporter.markdown(report)}
for name,key in [('results.csv','rows'),('attempts.csv','all_attempts')]:
 with(public/'results'/name).open(newline='')as f:fields=next(csv.reader(f))
 outputs[name]=reporter.csv_bytes(report[key],fields)
 if outputs[name]!=(public/'results'/name).read_bytes():raise ValueError('Exact CSV differs')
if outputs['report.md']!=(public/'results/report.md').read_bytes():raise ValueError('Exact report Markdown differs')
if any(x=='otqa'or x.startswith('otqa.')for x in sys.modules):raise ValueError('Solver imported')
out.mkdir(parents=True,exist_ok=False)
for name,data in outputs.items():
 with(out/name).open('xb')as f:f.write(data)
proof={'status':'provisional_offline_reproduction_pass','report_comparison':comparison,'correct':correct,'regular_unsolved':unsolved,'answers_checked_exact_fraction':answers,'primary_cells':100,'all_attempts':100,'original_A3_Raw_status_preserved':None if meta['A3_issue']is None else'provisional_failed','A3_full_Raw_calls':0,'solver_executed':False,'remote_access':False,'scientific_completion':False,'publication_completion':False}
with(out/'reproduction-verification.json').open('x')as f:json.dump(proof,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(proof,sort_keys=True))
