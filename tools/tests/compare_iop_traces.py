#!/usr/bin/env python3
"""Compare IOP pre-instruction traces (plain TXT or ZIP chunks)."""
import argparse
import json
import re
import zipfile

FIELD=re.compile(r'\b(N|PC|OP|HI|LO|R(?:0[0-9]|[12][0-9]|3[01]))=([0-9A-Fa-f]+)\b')
FIELDS=['PC','OP','HI','LO']+[f'R{i:02}' for i in range(32)]

def parse(line):
    if '[IOP]' not in line:
        return None
    values={k:int(v,10 if k=='N' else 16) for k,v in FIELD.findall(line)}
    if 'N' not in values:
        return None
    missing=[k for k in FIELDS if k not in values]
    if missing:
        raise ValueError(f'Incomplete IOP trace record N={values["N"]}: {missing}')
    return values

def records(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for name in sorted(n for n in z.namelist() if n.lower().endswith('.txt')):
                with z.open(name) as stream:
                    for line in stream:
                        row=parse(line.decode('ascii',errors='replace'))
                        if row is not None:
                            yield row
    else:
        with open(path,encoding='utf-8',errors='replace') as stream:
            for line in stream:
                row=parse(line)
                if row is not None:
                    yield row

def compare(reference,candidate,limit=None):
    a,b=iter(records(reference)),iter(records(candidate))
    count=0
    while limit is None or count<limit:
        x,y=next(a,None),next(b,None)
        if x is None or y is None:
            return dict(status='match' if x is None and y is None else 'length_mismatch',
                        compared=count, reference_exhausted=x is None,
                        candidate_exhausted=y is None)
        if x['N']!=y['N']:
            return dict(status='index_mismatch',compared=count,
                        reference_n=x['N'],candidate_n=y['N'])
        diff={k:dict(reference=f'{x[k]:08X}',candidate=f'{y[k]:08X}')
              for k in FIELDS if x[k]!=y[k]}
        if diff:
            return dict(status='divergence',compared=count,n=x['N'],differences=diff)
        count+=1
    return dict(status='limit_reached',compared=count)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference',help='PCSX2 trace TXT/ZIP')
    p.add_argument('candidate',help='PS3 trace TXT/ZIP')
    p.add_argument('--limit',type=int)
    args=p.parse_args()
    result=compare(args.reference,args.candidate,args.limit)
    print(json.dumps(result,indent=2))
    raise SystemExit(1 if result['status'] in ('divergence','index_mismatch','length_mismatch') else 0)
