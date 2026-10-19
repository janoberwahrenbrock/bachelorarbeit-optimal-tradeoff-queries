"""Saved integrity and table reproduction only; no new scientific computation."""
import argparse,hashlib,json,sys,types
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();root=a.project_root.resolve(strict=True);out=a.output.absolute();meta=json.loads((Path(__file__).parent/'reproduction.json').read_bytes());r=meta.pop('view');b=(root/r['path']).read_bytes()
if len(b)!=r['bytes']or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Exact saved-view source differs')
if out.exists()or out.is_symlink()or out.resolve(strict=False).is_relative_to(root):raise ValueError('Fresh output outside original extraction required')
m=types.ModuleType('published_E6_saved_view');m.__file__=str(root/r['path']);exec(compile(b,m.__file__,'exec'),m.__dict__);proof=m.verify_saved(root,meta)
if any(n=='otqa'or n.startswith('otqa.')for n in sys.modules):raise ValueError('Solver import refused')
out.mkdir(parents=True,exist_ok=False)
for name,data in {'results.json':m.encoded(meta['expected_report']),'results.csv':m.rows_csv(meta['expected_report']),'report.md':m.markdown(meta['expected_report']),'reproduction-verification.json':m.encoded(proof)}.items():
 with(out/name).open('xb')as f:f.write(data)
print(json.dumps(proof,sort_keys=True))
