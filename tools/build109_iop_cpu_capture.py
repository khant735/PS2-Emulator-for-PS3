#!/usr/bin/env python3
"""Build 109: explicit IOP diagnostic CPU checkpoint capture. No restore."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h";c=root/"source/emu_core.cpp"
def patch(p,old,new):
 s=p.read_text()
 if s.count(old)!=1:raise SystemExit("Build109 anchor mismatch "+str(p)+" "+repr(old))
 p.write_text(s.replace(old,new,1))
patch(h,"bool captureEeCpu(EeCpuCheckpoint& out) const;", """bool captureEeCpu(EeCpuCheckpoint& out) const;
 struct IopCpuCheckpoint {
  uint32_t version,pc,next,last_opcode,gpr[32],cop0[32],hi,lo;
  uint64_t instructions;
  uint32_t running,delay;
 };
 bool captureIopCpu(IopCpuCheckpoint& out) const;""")
patch(c,"Core::Core():", """bool Core::captureIopCpu(IopCpuCheckpoint& out) const {
 memset(&out,0,sizeof(out));
 out.version=1;
 out.pc=iop_pc;out.next=iop_next;out.last_opcode=iop_last_opcode;
 memcpy(out.gpr,iop_gpr,sizeof(iop_gpr));
 memcpy(out.cop0,iop_cop0,sizeof(iop_cop0));
 out.hi=iop_hi;out.lo=iop_lo;
 out.instructions=iop_instructions;
 out.running=iop_running?1u:0u;out.delay=iop_delay?1u:0u;
 return true;
}
Core::Core():""")
print("Build109: IOP CPU capture method added; restore remains disabled")
