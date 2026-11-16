#!/usr/bin/env python3
"""Build 158: initial IOP SIF status reads backed by EE SIF state.

Deliberately limited: no fabricated IOP writes, IRQ, DMA, or SIF RPC.
0x1D000020 and 0x1D000030 are IOP-side flag register offsets.
"""
from pathlib import Path

p=Path("src/PS2-PS3-Bringup-035-SOURCE/source/emu_core.cpp")
s=p.read_text()
anchor="  if(!src&&pa==0x1f80825cu){"
assert s.count(anchor)==1, "Build158 IOP LW dispatch anchor mismatch"
insert="""  // Build158: IOP-side SIF flag reads share the existing EE-side latches.
  // Read-only first stage; writes, DMA, IRQ and handshake semantics remain TODO.
  if(!src&&(pa==0x1d000020u||pa==0x1d000030u)){
    iop_gpr[rt]=(pa==0x1d000020u)?ee_sif_f2xx[1]:ee_sif_f230;
    iop_lw_value=iop_gpr[rt];++iop_lw_reads;iop_lw_reject=0;
  }else if(!src&&pa==0x1f80825cu){"""
s=s.replace(anchor,insert,1)
p.write_text(s)
print("Build158: IOP SIF flag read bridge installed")
