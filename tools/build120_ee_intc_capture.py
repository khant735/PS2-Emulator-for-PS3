#!/usr/bin/env python3
"""Build 120: capture EE interrupt controller registers, read-only.
This does not enable restore or imply complete interrupt scheduling.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h";c=root/"source/emu_core.cpp"
def patch(p,old,new):
 s=p.read_text()
 if s.count(old)!=1:raise SystemExit("Build120 anchor mismatch "+str(p)+" "+repr(old))
 p.write_text(s.replace(old,new,1))
patch(h,"bool captureEeTimers(EeTimerCheckpoint& out) const;",
"""bool captureEeTimers(EeTimerCheckpoint& out) const;
 struct EeIntcCheckpoint {
  uint32_t version,stat,mask;
 };
 bool captureEeIntc(EeIntcCheckpoint& out) const;""")
patch(c,"Core::Core():",
"""bool Core::captureEeIntc(EeIntcCheckpoint& out) const {
 memset(&out,0,sizeof(out));
 out.version=1;
 out.stat=intc_stat;out.mask=intc_mask;
 return true;
}
Core::Core():""")
print("Build120: read-only EE INTC register capture; restore disabled")
