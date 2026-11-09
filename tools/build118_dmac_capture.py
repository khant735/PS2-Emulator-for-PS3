#!/usr/bin/env python3
"""Build 118: capture existing EE DMAC diagnostic register state.
Read-only capture. Does not claim DMA transfer engine or restoration.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h";c=root/"source/emu_core.cpp"
def patch(p,old,new):
 s=p.read_text()
 if s.count(old)!=1:raise SystemExit("Build118 anchor mismatch "+str(p)+" "+repr(old))
 p.write_text(s.replace(old,new,1))
patch(h,"bool captureCpuAndMainRam(EeCpuCheckpoint& ee,IopCpuCheckpoint& iop,",
"""struct EeDmacCheckpoint {
 uint32_t version;
 uint32_t channel[10][7];
 uint32_t global[6];
 };
 bool captureEeDmac(EeDmacCheckpoint& out) const;
 bool captureCpuAndMainRam(EeCpuCheckpoint& ee,IopCpuCheckpoint& iop,""")
patch(c,"Core::Core():",
"""bool Core::captureEeDmac(EeDmacCheckpoint& out) const {
 memset(&out,0,sizeof(out));
 out.version=1;
 memcpy(out.channel,dmac_channel_regs,sizeof(out.channel));
 memcpy(out.global,dmac_global_regs,sizeof(out.global));
 return true;
}
Core::Core():""")
print("Build118: read-only EE DMAC register capture added; restore disabled")
