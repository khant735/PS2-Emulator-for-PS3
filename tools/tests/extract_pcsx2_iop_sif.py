#!/usr/bin/env python3
"""Extract SIF memory operations from a PCSX2 direct IOP trace ZIP.

Records are PRE-instruction snapshots. For loads, the next record contains
the loaded register value (except where a load-delay or interrupt complicates
the comparison). This utility never invents MMIO side effects.
"""
import argparse
import collections
import json
import re
import zipfile

RE = re.compile(r"\[IOP\] N=(\d+) PC=([0-9A-F]{8}) OP=([0-9A-F]{8})")
REG = re.compile(r"R(\d\d)=([0-9A-F]{8})")
MEM_OPS = {0x20:'LB',0x21:'LH',0x23:'LW',0x24:'LBU',0x25:'LHU',
           0x28:'SB',0x29:'SH',0x2B:'SW'}
def signed16(v):
    return v-0x10000 if v&0x8000 else v

def extract(path, limit=100):
    counts=collections.Counter()
    samples=[]
    previous=None
    with zipfile.ZipFile(path) as z:
        for name in sorted(n for n in z.namelist() if n.endswith('.txt')):
            with z.open(name) as stream:
                for raw in stream:
                    line=raw.decode('ascii', errors='replace')
                    m=RE.search(line)
                    if not m:
                        continue
                    n,pc,op=int(m[1]),int(m[2],16),int(m[3],16)
                    regs={int(k):int(v,16) for k,v in REG.findall(line)}
                    if previous is not None and previous['n']+1==n:
                        # The trace records state BEFORE each instruction.
                        if previous['type'] in ('LB','LH','LW','LBU','LHU'):
                            previous['next_rt']=f"{regs.get(previous['rt'],0):08X}"
                    previous=None
                    kind=MEM_OPS.get(op>>26)
                    if kind is None or len(regs)!=32:
                        continue
                    rs=(op>>21)&31
                    rt=(op>>16)&31
                    addr=(regs[rs]+signed16(op&0xffff))&0xffffffff
                    phys=addr&0x1fffffff
                    if not 0x1d000000<=phys<=0x1d0000ff:
                        continue
                    key=f"{phys:08X} {kind}"
                    counts[key]+=1
                    event={'n':n,'pc':f"{pc:08X}",'op':f"{op:08X}",
                           'type':kind,'vaddr':f"{addr:08X}",
                           'phys':f"{phys:08X}",'rt':rt,
                           'rt_before':f"{regs[rt]:08X}"}
                    if len(samples)<limit:
                        samples.append(event)
                        previous=event
    return {'counts':dict(sorted(counts.items())),
            'first_events':samples,'note':'next_rt is next pre-instruction state, not guaranteed MMIO read return'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('trace_zip')
    p.add_argument('--samples',type=int,default=100)
    p.add_argument('--output')
    args=p.parse_args()
    result=extract(args.trace_zip,args.samples)
    data=json.dumps(result,indent=2)+'\n'
    if args.output:
        with open(args.output,'w') as f:f.write(data)
    else:
        print(data)
