"""Portable stored-data reproduction; Python stdlib only, no solver or network."""
import argparse,csv,hashlib,json,sys,types
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=a.project_root.resolve(strict=True);out=a.output.absolute();repro=Path(__file__).resolve().parent
if out.exists() or out.is_symlink():raise ValueError('Fresh reproduction output required')
meta=json.loads((repro/'reproduction.json').read_bytes());public=root/meta['public_root']
def load(role,name=None):
 r=meta['tools'][role];f=root/r['path'];b=f.read_bytes()
 if f.is_symlink() or len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Frozen reproduction code differs')
 m=types.ModuleType(name or f.stem);m.__file__=str(f);exec(compile(b,str(f),'exec'),m.__dict__);return m
contract_name=Path(meta['tools']['contract']['path']).stem
if contract_name in sys.modules:raise ValueError('Unexpected preloaded contract')
sys.modules[contract_name]=load('contract',contract_name)
reporter=load('reporter');checker=load('raw');compare=load('compare')
reference=json.loads((public/'results/results.json').read_bytes());report=reporter.analyze(root,meta['series_path']);comparison=compare.compare(reference,report)
raw=checker.verify_study(root,meta['series_path'],root/meta['finish_proof'],root/meta['wheel'],public/'provenance/input-contract.json')
def core(value):
 d={k:v for k,v in value.items() if k not in ('created_at_utc','elapsed_seconds')}
 d['verified_read_artifacts']=sorted((r for r in d['verified_read_artifacts'] if r['path']!='@prepared_input_contract'),key=lambda r:r['path']);return d
expected=json.loads((public/'provenance/original-raw-check.json').read_bytes())
if raw['status']!='provisional_pass' or raw['findings'] or core(raw)!=core(expected):raise ValueError('Stored raw evidence comparison differs')
projection=json.loads((public/'provenance/selection-and-authorization.json').read_bytes());history=projection.get('technical_history')
if history is not None:
 if history['new_logical_quality_case'] or history['original_complete_total_api_seconds'] is not None or history['original_complete_total_controller_seconds'] is not None:raise ValueError('Historical unknown costs/credit changed')
 for index,item in enumerate(history['archived_original_attempt_prefixes']):
  data=(root/item['archive_journal_path']).read_bytes();progress=json.loads((root/item['archive_progress_path']).read_bytes());jr=item['journal']
  if len(data)!=jr['bytes'] or hashlib.sha256(data).hexdigest()!=jr['sha256'] or hashlib.sha256(data[:item['committed_prefix_bytes']]).hexdigest()!=item['committed_prefix_sha256']:raise ValueError('Historical original journal/prefix differs')
  count=sum(json.loads(line)['event_type']=='answer_received' for line in data[:item['committed_prefix_bytes']].splitlines())
  if count!=[2,0][index] or item['credit_to_relocated_attempt']!=0 or item['complete_API_seconds'] is not None or item['complete_controller_seconds'] is not None or progress['query_counts']['answered_total']!=count:raise ValueError('Historical technical prefix received incorrect credit')
outputs={'results.json':reporter.encoded(report),'report.md':reporter.markdown(report)}
for name,key in [('results.csv','rows'),('attempts.csv','all_attempts')]:
 with (public/'results'/name).open(newline='') as f:fields=next(csv.reader(f))
 outputs[name]=reporter.csv_bytes(report[key],fields)
 if outputs[name]!=(public/'results'/name).read_bytes():raise ValueError('CSV differs: '+name)
if outputs['report.md']!=(public/'results/report.md').read_bytes():raise ValueError('Markdown differs')
if any(n=='otqa' or n.startswith('otqa.') for n in sys.modules):raise ValueError('Solver package imported')
out.mkdir(parents=True,exist_ok=False)
for name,data in outputs.items():
 with (out/name).open('xb') as f:f.write(data)
receipt={'status':'provisional_offline_reproduction_pass','report_comparison':comparison,'raw_counts':raw['counts'],'solver_executed':False,'remote_access':False,'scientific_completion':False,'publication_completion':False,'raw_contract_projection':'Only @prepared_input_contract identity differs; unchanged verifier validates own exact frozen case IDs/config/dataset/suite','volatile_raw_fields':['created_at_utc','elapsed_seconds'],'all_other_raw_fields_compared':True}
with (out/'reproduction-verification.json').open('x') as f:json.dump(receipt,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(receipt,sort_keys=True))
