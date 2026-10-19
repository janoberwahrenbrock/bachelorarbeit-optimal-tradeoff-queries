"""Portable stdlib reproduction; no native package or remote access."""
import argparse,csv,json,runpy,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=a.project_root.absolute();out=a.output.absolute()
if out.exists() or out.is_symlink():raise ValueError('Reproduction output must be fresh')
meta=json.loads((Path(__file__).parent/'reproduction.json').read_text());public=root/meta['public_root'];repro=public/'reproduction'
reporter=runpy.run_path(str(repro/'single_study_report.py'));checker=runpy.run_path(str(repro/'verify_study_raw.py'));compare=runpy.run_path(str(repro/'compare_analysis.py'))
report=reporter['analyze'](root,meta['series_path']);reference=json.loads((public/'results/results.json').read_text());comparison=compare['compare'](reference,report)
raw=checker['verify_study'](root,meta['series_path'],root/meta['finish_proof'],root/meta['wheel'],public/'provenance/input-contract.json')
def core(value):
 result={k:v for k,v in value.items() if k not in ('created_at_utc','elapsed_seconds')}
 if 'verified_read_artifacts' in result:result['verified_read_artifacts']=sorted(result['verified_read_artifacts'],key=lambda r:r['path'])
 return result
expected_raw=json.loads((public/'provenance/raw-check.json').read_text())
if raw['status']!='provisional_pass' or core(raw)!=core(expected_raw):raise ValueError('Independent raw-check reproduction differs')
outputs={'results.json':reporter['encoded'](report),'report.md':reporter['markdown'](report)}
for name,key in [('results.csv','rows'),('attempts.csv','all_attempts')]:
 with (public/'results'/name).open(newline='') as f:fields=next(csv.reader(f))
 outputs[name]=reporter['csv_bytes'](report[key],fields)
 if outputs[name]!=(public/'results'/name).read_bytes():raise ValueError('Reproduced CSV differs: '+name)
if outputs['report.md']!=(public/'results/report.md').read_bytes():raise ValueError('Reproduced report markdown differs')
if any(n=='otqa' or n.startswith('otqa.') for n in sys.modules):raise ValueError('Native package unexpectedly imported')
out.mkdir(parents=True,exist_ok=False)
for name,data in outputs.items():
 with (out/name).open('xb') as f:f.write(data)
receipt={'status':'provisional_offline_reproduction_pass','report_comparison':comparison,'raw_counts':raw['counts'],'scientific_completion':False,'publication_completion':False,'solver_executed':False,'remote_access':False,'volatile_raw_fields':['created_at_utc','elapsed_seconds'],'raw_artifact_order':'sorted by portable path only; all identities/hashes/bytes compared'}
with (out/'reproduction-verification.json').open('x') as f:json.dump(receipt,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(receipt,sort_keys=True))
