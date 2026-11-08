#!/usr/bin/env python3
"""Build 065: capture 128-bit VIF0 FIFO ingress at physical 0x10004000."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 065 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vif0_regs[15];","uint64_t vif0_fifo_qwords,vif0_fifo_last_lo,vif0_fifo_last_hi;uint32_t vif0_regs[15];")
p=root/"source/emu_core.cpp"
change(p,"memset(vif0_regs,0,sizeof(vif0_regs));","vif0_fifo_qwords=vif0_fifo_last_lo=vif0_fifo_last_hi=0;memset(vif0_regs,0,sizeof(vif0_regs));")
change(p,"  // VIF1 FIFO at physical 0x10005000 accepts 128-bit SQ ingress.",'''  // VIF0 FIFO at physical 0x10004000 accepts 128-bit SQ ingress.
  // Capture only; no VIF packet execution, DMA, interrupts or FIFO drain.
  if(!p && store){
   uint32_t vif0_fifo_physical=0;
   if(translate(aligned,16,true,vif0_fifo_physical) &&
      vif0_fifo_physical==0x10004000u){
    vif0_fifo_last_lo=rt?reg[rt]:0;
    vif0_fifo_last_hi=rt?reg_hi[rt]:0;
    ++vif0_fifo_qwords;
    p=(unsigned char*)1; // Existing FIFO sentinel prevents normal RAM writes.
   }
  }
  // VIF1 FIFO at physical 0x10005000 accepts 128-bit SQ ingress.''')
change(p,'fprintf(f,"VIF1 FIFO ingress (capture only;', 'fprintf(f,"VIF0 FIFO ingress (capture only; no VIF parsing/DMA/IRQ): QWORDS=%llu LAST_LO=%016llX LAST_HI=%016llX\\n",(unsigned long long)vif0_fifo_qwords,(unsigned long long)vif0_fifo_last_lo,(unsigned long long)vif0_fifo_last_hi);\n fprintf(f,"VIF1 FIFO ingress (capture only;')
change(root/"source/emu_ui.inc","BUILD 064 - VIF0 REGISTERS","BUILD 065 - VIF0 FIFO INGRESS")
print("Build 065 VIF0 FIFO ingress capture applied")
