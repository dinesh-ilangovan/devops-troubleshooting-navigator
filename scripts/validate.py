from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent
files=[ROOT/'data/kubernetes.json',ROOT/'data/docker.json']
R=[]
for f in files:
    x=json.loads(f.read_text(encoding='utf-8')); R+=x
errors=[]
if len(R)!=961: errors.append(f'Expected 961 scenarios, got {len(R)}')
ids=[x.get('id') for x in R]
if len(ids)!=len(set(ids)): errors.append('Duplicate scenario IDs')
for x in R:
    if not x.get('title'): errors.append(f"{x.get('id')}: missing title")
    if len(x.get('branches',[]))!=3: errors.append(f"{x.get('id')}: expected 3 branches")
    if len(x.get('all_walkthroughs',[]))!=6: errors.append(f"{x.get('id')}: expected 6 walkthroughs")
    for i,w in enumerate(x.get('all_walkthroughs',[]),1):
        for k in ['case','check','output','root','fix','verify','verified']:
            if not w.get(k): errors.append(f"{x.get('id')} walkthrough {i}: missing {k}")
if errors:
    print('VALIDATION FAILED'); print('\n'.join(errors[:100])); sys.exit(1)
print('VALIDATION PASSED')
print(f'Scenarios: {len(R)} | Walkthroughs: {sum(len(x["all_walkthroughs"]) for x in R)}')
