import json, sys

with open('test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total   = len(data)
perfect = sum(1 for v in data.values() if v['quality']['quality_score'] >= 80)
good    = sum(1 for v in data.values() if 50 <= v['quality']['quality_score'] < 80)
poor    = sum(1 for v in data.values() if v['quality']['quality_score'] < 50)
zero    = [k for k, v in data.items() if v['quality']['jobs_found'] == 0]

lines = []
lines.append(f'Total: {total}  |  Excellent(>=80): {perfect}  |  Good(50-79): {good}  |  Poor(<50): {poor}')
lines.append('')
for fname, res in sorted(data.items(), key=lambda x: x[1]['quality']['quality_score']):
    q = res['quality']
    jobs = res['jobs']
    score = q['quality_score']
    flag = 'OK' if score >= 80 else ('MED' if score >= 50 else 'BAD')
    lines.append(f'[{flag}][{score:3d}] {fname[:55]:<55} jobs={q["jobs_found"]}')
    for issue in q['issues']:
        lines.append(f'         {issue}')
    for j in jobs[:2]:
        company = j.get('company_name') or '(no company)'
        title   = j.get('job_title') or '(no title)'
        lines.append(f'         >> {title[:40]:<40} @ {company[:30]}')
lines.append('')
if zero:
    lines.append('ZERO JOBS:')
    for z in zero:
        lines.append(f'  - {z}')

output = '\n'.join(lines)
print(output)

with open('results_summary.txt', 'w', encoding='utf-8') as f:
    f.write(output)
