from pathlib import Path
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parent.parent
K=json.loads((ROOT/'src/kubernetes.json').read_text(encoding='utf-8'))
D=json.loads((ROOT/'src/docker.json').read_text(encoding='utf-8'))
R=K+D
assert len(K)==520, f"Expected 520 Kubernetes, got {len(K)}"
assert len(D)==441, f"Expected 441 Docker, got {len(D)}"
assert len(R)==961
ids=[x['id'] for x in R]; assert len(ids)==len(set(ids)), 'Duplicate IDs'
assert all(len(x.get('all_walkthroughs',[]))==6 for x in R), 'Each scenario must have 6 walkthroughs'
assert sum(len(x['all_walkthroughs']) for x in R)==5766
required=['title','technology','category','steps','branches','all_walkthroughs']
assert all(all(k in x for k in required) for x in R)
payload=json.dumps(R,separators=(',',':'),ensure_ascii=False).replace('</script>','<\\/script>')
t=(ROOT/'app/navigator.template.html').read_text(encoding='utf-8')
assert t.count('__SCENARIO_DATA__')==1
html=t.replace('__SCENARIO_DATA__',payload)
dist=ROOT/'dist/DevOps_Troubleshooting_Navigator.html'
dist.write_text(html,encoding='utf-8')
# output integrity
mm=re.search(r'<script id="scenario-data" type="application/json">(.*?)</script>',html,re.S)
RR=json.loads(mm.group(1)); assert len(RR)==961
scripts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',html,re.S)
check=ROOT/'dist/_check.js'; check.write_text(scripts[-1],encoding='utf-8')
r=subprocess.run(['node','--check',str(check)],capture_output=True,text=True)
check.unlink(missing_ok=True)
assert r.returncode==0,r.stderr
assert html.rstrip().endswith('</html>')
print('BUILD PASSED')
print('Kubernetes:',len(K)); print('Docker:',len(D)); print('Scenarios:',len(R)); print('Walkthroughs:',sum(len(x['all_walkthroughs']) for x in R)); print(dist)
