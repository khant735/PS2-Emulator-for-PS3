#!/usr/bin/env python3
"""Build 108: expose explicit EE CPU checkpoint capture (no unsafe restore)."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"
def replace(p,old,new):
 s=p.read_text()
 if s.count(old)!=1:raise SystemExit("Build108 anchor mismatch: "+str(p)+" "+repr(old))
 p.write_text(s.replace(old,new,1))
replace(h,"Core(); ~Core(); bool ready() const;", """// Pointer-free EE CPU checkpoint, versioned separately from machine state.
 struct EeCpuCheckpoint {
  uint32_t version,pc,next,opcode,stop,cp0[32],fpr[32];
  uint64_t reg[32],reg_hi[32],instructions,hi,lo;
  uint32_t intc_stat,intc_mask;
 };
 bool captureEeCpu(EeCpuCheckpoint& out) const;
 Core(); ~Core(); bool ready() const;""")
replace(c,"Core::Core():", """bool Core::captureEeCpu(EeCpuCheckpoint& out) const {
 memset(&out,0,sizeof(out));
 out.version=1;
 out.pc=pc;out.next=next;out.opcode=opcode;out.stop=(uint32_t)stop;
 memcpy(out.cp0,cp0,sizeof(cp0));memcpy(out.fpr,fpr,sizeof(fpr));
 memcpy(out.reg,reg,sizeof(reg));memcpy(out.reg_hi,reg_hi,sizeof(reg_hi));
 out.instructions=instructions;out.hi=hi;out.lo=lo;
 out.intc_stat=intc_stat;out.intc_mask=intc_mask;
 return true;
}
Core::Core():""")
print("Build108: EE CPU checkpoint capture method added; restore remains disabled")
